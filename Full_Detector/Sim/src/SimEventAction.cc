//
// ********************************************************************
// * License and Disclaimer                                           *
// *                                                                  *
// * The  Geant4 software  is  copyright of the Copyright Holders  of *
// * the Geant4 Collaboration.  It is provided  under  the terms  and *
// * conditions of the Geant4 Software License,  included in the file *
// * LICENSE and available at  http://cern.ch/geant4/license .  These *
// * include a list of copyright holders.                             *
// *                                                                  *
// * Neither the authors of this software system, nor their employing *
// * institutes,nor the agencies providing financial support for this *
// * work  make  any representation or  warranty, express or implied, *
// * regarding  this  software system or assume any liability for its *
// * use.  Please see the license in the file  LICENSE  and URL above *
// * for the full disclaimer and the limitation of liability.         *
// *                                                                  *
// * This  code  implementation is the result of  the  scientific and *
// * technical work of the GEANT4 collaboration.                      *
// * By using,  copying,  modifying or  distributing the software (or *
// * any work based  on the software)  you  agree  to acknowledge its *
// * use  in  resulting  scientific  publications,  and indicate your *
// * acceptance of all terms of the Geant4 Software license.          *
// ********************************************************************
//
//
/// \file optical/Sim/src/SimEventAction.cc
/// \brief Implementation of the SimEventAction class
//
//
#include "SimEventAction.hh"
#include "SimScintHit.hh"
#include "SimPMTHit.hh"
#include "SimTrajectory.hh"
#include "SimRun.hh"
#include "SimHistoManager.hh"
#include "SimDetectorConstruction.hh"

#include "G4EventManager.hh"
#include "G4SDManager.hh"
#include "G4RunManager.hh"
#include "G4Event.hh"
#include "G4EventManager.hh"
#include "G4TrajectoryContainer.hh"
#include "G4Trajectory.hh"
#include "G4VVisManager.hh"
#include "G4ios.hh"
#include "G4UImanager.hh"
#include "G4SystemOfUnits.hh"

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

SimEventAction::SimEventAction(const SimDetectorConstruction* det)
  : fDetector(det),fScintCollID(-1),fPMTCollID(-1),fVerbose(0),
   fPMTThreshold(1),fForcedrawphotons(false),fForcenophotons(false)
{
  fEventMessenger = new SimEventMessenger(this);

  fHitCount = 0;
  fPhotonCount_Scint = 0;
  fPhotonCount_Ceren = 0;
  fAbsorptionCount = 0;
  fBoundaryAbsorptionCount = 0;
  fTotE = 0.0;
  fSilicon1eCounter = 0;
  fSilicon2eCounter = 0;

  fConvPosSet = false;
  fEdepMax = 0.0;

  fPMTsAboveThreshold = 0;
}
 
//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

SimEventAction::~SimEventAction(){}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimEventAction::BeginOfEventAction(const G4Event*) {
 
  fHitCount = 0;
  fPhotonCount_Scint = 0;
  fPhotonCount_Ceren = 0;
  fAbsorptionCount = 0;
  fBoundaryAbsorptionCount = 0;
  fTotE = 0.0;
  fSilicon1eCounter = 0;
  fSilicon2eCounter = 0;

  fConvPosSet = false;
  fEdepMax = 0.0;

  fPMTsAboveThreshold = 0;

  G4SDManager* SDman = G4SDManager::GetSDMpointer();
  if(fScintCollID<0)
    fScintCollID=SDman->GetCollectionID("scintCollection");
  if(fPMTCollID<0)
    fPMTCollID=SDman->GetCollectionID("pmtHitCollection");
}
 
//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimEventAction::EndOfEventAction(const G4Event* anEvent){

  G4TrajectoryContainer* trajectoryContainer=anEvent->GetTrajectoryContainer();
 
  G4int n_trajectories = 0;
  if (trajectoryContainer) n_trajectories = trajectoryContainer->entries();

  // extract the trajectories and draw them
  if (G4VVisManager::GetConcreteInstance()){
    for (G4int i=0; i<n_trajectories; i++){
      SimTrajectory* trj = (SimTrajectory*)
        ((*(anEvent->GetTrajectoryContainer()))[i]);
      if(trj->GetParticleName()=="opticalphoton"){
        trj->SetForceDrawTrajectory(fForcedrawphotons);
        trj->SetForceNoDrawTrajectory(fForcenophotons);
      }
      trj->DrawTrajectory();
    }
  }
 
  SimScintHitsCollection* scintHC = nullptr;
  SimPMTHitsCollection* pmtHC = nullptr;
  G4HCofThisEvent* hitsCE = anEvent->GetHCofThisEvent();
 
  //Get the hit collections
  if(hitsCE){
    if(fScintCollID>=0) {
      scintHC = (SimScintHitsCollection*)(hitsCE->GetHC(fScintCollID));
    }
    if(fPMTCollID>=0) {
      pmtHC = (SimPMTHitsCollection*)(hitsCE->GetHC(fPMTCollID));
    }
  }

  //Hits in scintillator
  if(scintHC){
    int n_hit = scintHC->entries();
    G4ThreeVector  eWeightPos(0.);
    G4double edep;
    G4double edepMax=0;

    for(int i=0;i<n_hit;i++){ //gather info on hits in scintillator
      edep=(*scintHC)[i]->GetEdep();
      fTotE += edep;
      eWeightPos += (*scintHC)[i]->GetPos()*edep;//calculate energy weighted pos
      if(edep>edepMax){
        edepMax=edep;//store max energy deposit
        G4ThreeVector posMax=(*scintHC)[i]->GetPos();
        fPosMax = posMax;
        fEdepMax = edep;
      }
    }
    
    G4AnalysisManager::Instance()->FillH1(7, fTotE);
    
    if(fTotE == 0.){
      if(fVerbose>0)G4cout<<"No hits in the scintillator this event."<<G4endl;
    }
    else{
      //Finish calculation of energy weighted position
      eWeightPos /= fTotE;
      fEWeightPos = eWeightPos; 
      if(fVerbose>0){
        G4cout << "\tEnergy weighted position of hits in Sim : "
               << eWeightPos/mm << G4endl;
      }
    }
    if(fVerbose>0){
    G4cout << "\tTotal energy deposition in scintillator : "
           << fTotE / keV << " (keV)" << G4endl;
    }
  }
 
  if(pmtHC){
    G4ThreeVector reconPos(0.,0.,0.);
    G4int pmts=pmtHC->entries();
    //Gather info from all PMTs
    for(G4int i=0;i<pmts;i++){
      fHitCount += (*pmtHC)[i]->GetPhotonCount();
      reconPos+=(*pmtHC)[i]->GetPMTPos()*(*pmtHC)[i]->GetPhotonCount();
      if((*pmtHC)[i]->GetPhotonCount()>=fPMTThreshold){
        fPMTsAboveThreshold++;
      }
      else{//wasnt above the threshold, turn it back off
        (*pmtHC)[i]->SetDrawit(false);
      }
    }

    G4AnalysisManager::Instance()->FillH1(1, fHitCount);
    G4AnalysisManager::Instance()->FillH1(2, fPMTsAboveThreshold);

    if(fHitCount > 0) {//dont bother unless there were hits
      reconPos/=fHitCount;
      if(fVerbose>0){
        G4cout << "\tReconstructed position of hits in Sim : "
               << reconPos/mm << G4endl;
      }
      fReconPos = reconPos;
    }
    pmtHC->DrawAllHits();
  }

  G4AnalysisManager::Instance()->FillH1(3, fPhotonCount_Scint);
  G4AnalysisManager::Instance()->FillH1(4, fPhotonCount_Ceren);
  G4AnalysisManager::Instance()->FillH1(5, fAbsorptionCount);
  G4AnalysisManager::Instance()->FillH1(6, fBoundaryAbsorptionCount);

  if(fVerbose>0){
    //End of event output. later to be controlled by a verbose level
    G4cout << "\tNumber of photons that hit PMTs in this event : "
           << fHitCount << G4endl;
    G4cout << "\tNumber of PMTs above threshold("<<fPMTThreshold<<") : "
           << fPMTsAboveThreshold << G4endl;
    G4cout << "\tNumber of photons produced by scintillation in this event : "
           << fPhotonCount_Scint << G4endl;
    G4cout << "\tNumber of photons produced by cerenkov in this event : "
           << fPhotonCount_Ceren << G4endl;
    G4cout << "\tNumber of photons absorbed (OpAbsorption) in this event : "
           << fAbsorptionCount << G4endl;
    G4cout << "\tNumber of photons absorbed at boundaries (OpBoundary) in "
           << "this event : " << fBoundaryAbsorptionCount << G4endl;
    G4cout << "Unaccounted for photons in this event : "
           << (fPhotonCount_Scint + fPhotonCount_Ceren -
                fAbsorptionCount - fHitCount - fBoundaryAbsorptionCount)
           << G4endl;
    G4cout << "Silicon slab no. 1 electron count: "
           << fSilicon1eCounter
           << G4endl;
    G4cout << "Silicon slab no. 2 electron count: "
           << fSilicon2eCounter
           << G4endl;
  }
  std::vector<G4int> pmts_vec;
  pmts_vec.resize(NUM_OF_PMTS);
  if (pmtHC)
  {
    G4int pmts = pmtHC->entries();
    //Gather info from all PMTs
    G4cout << (*pmtHC).GetVector()->size() << G4endl;
    for (G4int i = 0; i < pmts; i++)
    {
      int index=0;
      int mod=0, div=0 ;
      G4cout << (*pmtHC)[i]->GetPMTPos() << G4endl;
      G4cout << "PMT-DATA: " << (*pmtHC)[i]->GetPMTPhysVol()->GetInstanceID() << " | " << (*pmtHC)[i]->GetPMTPhysVol()->GetTranslation() << " | " << (*pmtHC)[i]->GetPhotonCount() << G4endl;

      // This is a fixed conversion from the pmt ID to it's index in the pmt's array. This is retarded
      // and I hope the people who wrote it have to read this code for eternity.
      // This assumes the PMTs are constructed in a very special way. If you move anything it will break.

      int id = (*pmtHC)[i]->GetPMTPhysVol()->GetInstanceID();

      int scint_num = (id - 4)/17;
      int scint_pmt_num = (id - 4)%17;
      int pmt_idx = 4*scint_num + scint_pmt_num;
      pmts_vec[pmt_idx] = (*pmtHC)[i]->GetPhotonCount();
/*
      index -= 4;
      mod = index%17;
      div = index/17;
      switch (mod) {
        case 3:
          pmts_vec[mod+div*4-3] = (*pmtHC)[i]->GetPhotonCount();
          break;
        case 2:
          pmts_vec[mod+div*4] = (*pmtHC)[i]->GetPhotonCount();
          break;
        case 1:
          pmts_vec[mod+div*4] = (*pmtHC)[i]->GetPhotonCount();
          break;
        case 0:
          pmts_vec[mod+div*4+3] = (*pmtHC)[i]->GetPhotonCount();
          break;
      }
*/
      //pmts_vec[mod+div*4] = (*pmtHC)[i]->GetPhotonCount();
    }
  }

  // update the run statistics
  SimRun* run = static_cast<SimRun*>(
    G4RunManager::GetRunManager()->GetNonConstCurrentRun());

  run->IncHitCount(fHitCount);
  run->IncPhotonCount_Scint(fPhotonCount_Scint);
  run->IncPhotonCount_Ceren(fPhotonCount_Ceren);
  run->IncEDep(fTotE);
  run->IncAbsorption(fAbsorptionCount);
  run->IncBoundaryAbsorption(fBoundaryAbsorptionCount);
  run->IncHitsAboveThreshold(fPMTsAboveThreshold);
  run->IncSilicon1eCounter(fSilicon1eCounter);
  run->IncSilicon2eCounter(fSilicon2eCounter);
  run->IncPMTS(pmts_vec);

  //If we have set the flag to save 'special' events, save here
  if(fPhotonCount_Scint + fPhotonCount_Ceren <= fDetector->GetSaveThreshold())
  {
    G4RunManager::GetRunManager()->rndmSaveThisEvent();
  }
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......
