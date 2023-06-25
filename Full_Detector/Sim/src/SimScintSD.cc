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
/// \file optical/Sim/src/SimScintSD.cc
/// \brief Implementation of the SimScintSD class
//
//
#include "SimScintSD.hh"
#include "SimScintHit.hh"
#include "G4VPhysicalVolume.hh"
#include "G4LogicalVolume.hh"
#include "G4Track.hh"
#include "G4Step.hh"
#include "G4ParticleDefinition.hh"
#include "G4VTouchable.hh"
#include "G4TouchableHistory.hh"
#include "G4ios.hh"
#include "G4VProcess.hh"
#include "FilePrinter.hh"
#include <G4ThreeVector.hh>

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

SimScintSD::SimScintSD(G4String name)
  : G4VSensitiveDetector(name)
{
  fScintCollection = nullptr;
  collectionName.insert("scintCollection");
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

SimScintSD::~SimScintSD() {}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimScintSD::Initialize(G4HCofThisEvent* hitsCE){
  fScintCollection = new SimScintHitsCollection
                      (SensitiveDetectorName,collectionName[0]);
  //A way to keep all the hits of this event in one place if needed
  static G4int hitsCID = -1;
  if(hitsCID<0){
    hitsCID = GetCollectionID(0);
  }
  hitsCE->AddHitsCollection( hitsCID, fScintCollection );
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......
G4bool SimScintSD::ProcessHits(G4Step* aStep,G4TouchableHistory* ){
  static G4double fTotalEnergy = 0;
  static G4ThreeVector current_location;
  static G4ThreeVector prev_location;
  static G4double range = 0;
  static G4double rho = 1.023; // specific! change for different setups
  static G4double let = 0;
  static G4double max_let = 0;
  G4double edep = aStep->GetTotalEnergyDeposit();
  if(edep==0.) return false; //No edep so dont count as hit

  if (aStep->GetTrack()->GetParentID() == 0)
  {
    G4StepPoint *preStep = aStep->GetPreStepPoint();
    std::stringstream& ss = FilePrinter::GetStreamForWrite();
    if (aStep->IsFirstStepInVolume() && preStep->GetStepStatus() == fGeomBoundary)
    {
      fTotalEnergy = 0;
      ss << "Particle Volume: " << aStep->GetTrack()->GetVolume()->GetLogicalVolume()->GetName() << G4endl;
      ss << "Particle Name: " << aStep->GetTrack()->GetParticleDefinition()->GetParticleName() << G4endl;
      ss << "Enter Location: " << (preStep->GetPosition()) << G4endl;
      G4cout << "Particle Volume: " << aStep->GetTrack()->GetVolume()->GetLogicalVolume()->GetName() << G4endl;
      G4cout << "Particle Name: " << aStep->GetTrack()->GetParticleDefinition()->GetParticleName() << G4endl;
      G4cout << "Enter Location: " << (preStep->GetPosition()) << G4endl;
      prev_location = preStep->GetPosition();
    }

    fTotalEnergy += edep;
    G4cout << "Current step energy: " << edep << G4endl;
    G4cout << "Total energy until current step: " << fTotalEnergy << G4endl;
    ss << "Total energy until current step: " << fTotalEnergy << G4endl;
    current_location = aStep->GetTrack()->GetPosition();
    range = (current_location - prev_location).mag();
    let = edep/range/rho/100;
    G4cout << "LET in current step: " << let << G4endl;
    ss << "LET in current step: " << let << G4endl;
    if (max_let < let) max_let = let;
    G4cout << "Max LET until current step: " << max_let << G4endl;
    ss << "Max LET until current step: " << max_let << G4endl;

    ss << "Current Location: " << aStep->GetTrack()->GetPosition() << G4endl;
    G4cout << "Current Location: " << aStep->GetTrack()->GetPosition() << G4endl;
    prev_location = current_location;

    if (aStep->IsLastStepInVolume())
    {
      ss << "Particle Volume: " << aStep->GetTrack()->GetVolume()->GetLogicalVolume()->GetName() << G4endl;
      G4cout << "Particle Volume: " << aStep->GetTrack()->GetVolume()->GetLogicalVolume()->GetName() << G4endl;
      ss << "Exit Location: " << aStep->GetTrack()->GetPosition() << G4endl;
      G4cout << "Exit Location: " << aStep->GetTrack()->GetPosition() << G4endl;
      ss << "Total energy deposited: " << fTotalEnergy << G4endl;
      G4cout << "Total energy deposited: " << fTotalEnergy << G4endl;
      G4cout << "Max LET: " << max_let << G4endl;
      ss << "Max LET: " << max_let << G4endl;

    }
  }

  G4StepPoint* thePrePoint = aStep->GetPreStepPoint();
  G4TouchableHistory* theTouchable =
    (G4TouchableHistory*)(aStep->GetPreStepPoint()->GetTouchable());
  G4VPhysicalVolume* thePrePV = theTouchable->GetVolume();
 
  G4StepPoint* thePostPoint = aStep->GetPostStepPoint();

  //Get the average position of the hit
  G4ThreeVector pos = thePrePoint->GetPosition() + thePostPoint->GetPosition();
  pos/=2.;

  SimScintHit* scintHit = new SimScintHit(thePrePV);

  scintHit->SetEdep(edep);
  scintHit->SetPos(pos);

  fScintCollection->insert(scintHit);

  return true;
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimScintSD::EndOfEvent(G4HCofThisEvent *) {}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimScintSD::clear() {} 

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimScintSD::DrawAll() {} 

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimScintSD::PrintAll() {} 
