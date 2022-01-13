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
/// \file optical/Sim/src/SimTrackingAction.cc
/// \brief Implementation of the SimTrackingAction class
//
//
#include "SimTrajectory.hh"
#include "SimTrackingAction.hh"
#include "SimUserTrackInformation.hh"
#include "SimDetectorConstruction.hh"
#include "SimEventAction.hh"

#include "G4TrackingManager.hh"
#include "G4Track.hh"
#include "G4ParticleTypes.hh"
#include "G4SystemOfUnits.hh"
#include "G4Box.hh"

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

SimTrackingAction::SimTrackingAction(SimDetectorConstruction* detector, SimEventAction* eAction)
{
  fDetector = detector;
  fEventAction = eAction;
  fTargetRegion = 0;
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimTrackingAction::PreUserTrackingAction(const G4Track* aTrack)
{
  //Let this be up to the user via vis.mac
  //  fpTrackingManager->SetStoreTrajectory(true);

const G4ParticleDefinition* particleDefinition = aTrack->GetParticleDefinition();
    if(particleDefinition == G4Electron::Definition()) //  || particleDefinition == G4Gamma::Definition())
    {
        if(fTargetRegion == 0) // target region is initialized after detector construction instantiation
        {
            fTargetRegion = fDetector->GetTargetRegion();
        }

        const G4ThreeVector& position = aTrack->GetPosition();

        int N =  fTargetRegion->GetNumberOfRootVolumes();
        std::vector<G4LogicalVolume*>::iterator it_logicalVolumeInRegion =
                fTargetRegion->GetRootLogicalVolumeIterator();

        bool inside_target_1 = false;
        bool inside_target_2 = false;

        for(int i = 0; i < N ; i++, it_logicalVolumeInRegion++)
        {
          if (i == 0)
          {
            EInside test_status = (*it_logicalVolumeInRegion)->GetSolid()->Inside(position - fDetector->GetvSilicon1Location());
            if (test_status == kInside)
            {
              inside_target_1 = true;
              break;
            }
          }

          if (i == 1)
          {
            EInside test_status = (*it_logicalVolumeInRegion)->GetSolid()->Inside(position - fDetector->GetvSilicon2Location());
            if (test_status == kInside)
            {
              inside_target_2 = true;
              break;
            }
          }
        }

        if(inside_target_1 == true)
        {
          fEventAction->IncSilicon1eCounter();
          fNParticleInTarget[particleDefinition]++;
        }
        else if (inside_target_2 == true)
        {
          fEventAction->IncSilicon2eCounter();
          fNParticleInTarget[particleDefinition]++;
        }
        else
        {
            fNParticleInWorld[particleDefinition]++;
        }
    }

  //Use custom trajectory class
  fpTrackingManager->SetTrajectory(new SimTrajectory(aTrack));

  //This user track information is only relevant to the photons
  fpTrackingManager->SetUserTrackInformation(new SimUserTrackInformation);
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimTrackingAction::PostUserTrackingAction(const G4Track* aTrack){
  SimTrajectory* trajectory =
    (SimTrajectory*)fpTrackingManager->GimmeTrajectory();
  SimUserTrackInformation*
    trackInformation=(SimUserTrackInformation*)aTrack->GetUserInformation();

  //Lets choose to draw only the photons that hit a pmt
  if(aTrack->GetDefinition()==G4OpticalPhoton::OpticalPhotonDefinition()){
    if (trackInformation->GetTrackStatus() & hitPMT)
      trajectory->SetDrawTrajectory(true);
  }
  else //draw all other trajectories
    trajectory->SetDrawTrajectory(true);

  if(trackInformation->GetForceDrawTrajectory())
    trajectory->SetDrawTrajectory(true);
}
