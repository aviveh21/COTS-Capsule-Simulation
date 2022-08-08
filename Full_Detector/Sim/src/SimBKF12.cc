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
/// 
/// brief Implementation of the SimBKF12 class
//
//
#include "globals.hh"

#include "SimBKF12.hh"

#include "G4LogicalSkinSurface.hh"
#include "G4LogicalBorderSurface.hh"

#include "G4SystemOfUnits.hh"
#include "G4SubtractionSolid.hh"

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

SimBKF12::SimBKF12(G4RotationMatrix *pRot,
                             const G4ThreeVector &tlate,
                             G4LogicalVolume *pMotherLogical,
                             G4bool pMany,
                             G4int pCopyNo,
                             SimDetectorConstruction* c)
  //Pass info to the G4PVPlacement constructor
  :G4PVPlacement(pRot,tlate,
                 //Temp logical volume must be created here
                 new G4LogicalVolume(new G4Box("temp",1,1,1),
                                     G4Material::GetMaterial("Vacuum"),
                                     "temp",0,0,0),
                 "housing",pMotherLogical,pMany,pCopyNo),fConstructor(c)
{
  CopyValues();
  G4double housing_x=fScint_x+2.*fD_mtl;
  G4double housing_y=fScint_y+2.*fD_mtl;
  G4double housing_z=detector_size_z;


  fHousing_box = new G4Box("housing_box_start", housing_x / 2., housing_y / 2., housing_z / 2.);
  
  fHousing_log = new G4LogicalVolume(fHousing_box,
                                     G4Material::GetMaterial("Air"),
                                     "housing_log",0,0,0);

  
  //Place the BKF12 (apoxy and Aluminum) on back and front of scintilator 
  epoxy_box = new G4Box("epoxy_box",  epoxy_size_x / 2.,  epoxy_size_y / 2., epoxy_size_z / 2.);

  epoxy_log = new G4LogicalVolume(epoxy_box,G4Material::GetMaterial("Epoxy"),
                                   "epoxy_log",0,0,0);
  
  aluminium_box = new G4Box("aluminium_box",  aluminium_size_x / 2.,  aluminium_size_y / 2., aluminium_size_z / 2.);

  aluminium_log = new G4LogicalVolume(aluminium_box,G4Material::GetMaterial("Al"),
                                   "aluminium_log",0,0,0);
  printf("catch_me!");
  // Notice - to place the BKF12 exectly at the middle - we need to add the half of the space in top and bottom of each detector
  // Thats because the spaces are NOT equal
  //Top BKF12
  new G4PVPlacement(0,G4ThreeVector(0., 0.,(Space_Top-Space_Down)/2.-fScint_z/2.-Space_Top-epoxy_size_z/ 2.),epoxy_log,"epoxy_top_2",
                                 fHousing_log,false,0);
  
  //new G4PVPlacement(0,G4ThreeVector(0., 0., (Space_Top-Space_Down)/2.-fScint_z/2.-Space_Top-epoxy_size_z-aluminium_size_z/ 2.),aluminium_log,"aluminium_top",
  //                               fHousing_log,false,0);
  
  new G4PVPlacement(0,G4ThreeVector(0., 0., (Space_Top-Space_Down)/2.-fScint_z/2.-Space_Top-epoxy_size_z-aluminium_size_z-epoxy_size_z / 2.),epoxy_log,"epoxy_top_1",
                                 fHousing_log,false,0);
  
  //Bottom BKF12
  new G4PVPlacement(0,G4ThreeVector(0., 0., (Space_Top-Space_Down)/2.+fScint_z/2.+Space_Down+epoxy_size_z / 2.),epoxy_log,"epoxy_bottom_1",
                                 fHousing_log,false,0);
  
  //new G4PVPlacement(0,G4ThreeVector(0., 0., (Space_Top-Space_Down)/2.+fScint_z/2.+Space_Down+epoxy_size_z+aluminium_size_z/ 2.),aluminium_log,"aluminium_bottom",
  //                               fHousing_log,false,0);
  
  new G4PVPlacement(0,G4ThreeVector(0., 0., (Space_Top-Space_Down)/2.+fScint_z/2.+Space_Down+epoxy_size_z+aluminium_size_z+epoxy_size_z / 2.),epoxy_log,"epoxy_bottom_2",
                                 fHousing_log,false,0);

  VisAttributes();

  SetLogicalVolume(fHousing_log);
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimBKF12::CopyValues(){
  fScint_x=fConstructor->GetScintX();
  fScint_y=fConstructor->GetScintY();
  fScint_z=fConstructor->GetScintZ();
  //new
  epoxy_size_x=fConstructor->GetepoxyX();
  epoxy_size_y=fConstructor->GetepoxyY();
  epoxy_size_z=fConstructor->GetepoxyZ();
  aluminium_size_x=fConstructor->GetaluminiumX();
  aluminium_size_y=fConstructor->GetaluminiumY();
  aluminium_size_z=fConstructor->GetaluminiumZ();
  Space_Down=fConstructor->Getspacedown();
  Space_Top=fConstructor->Getspacetop();
  detector_size_z = fConstructor->GetdetectorsizeZ();

  fD_mtl=fConstructor->GetHousingThickness();
  fNx=fConstructor->GetNX();
  fNy=fConstructor->GetNY();
  fNz=fConstructor->GetNZ();
  fRefl=fConstructor->GetHousingReflectivity();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......



//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimBKF12::VisAttributes(){
  fHousing_log->SetVisAttributes(G4VisAttributes::GetInvisible());

  //G4VisAttributes* housing_va = new G4VisAttributes(G4Colour(1.0,0.0,1.0));
  //fHousing_log->SetVisAttributes(housing_va);
  //G4VisAttributes* epoxy_va = new G4VisAttributes(G4Colour(0.0,1.0,1.0));
  //epoxy_log->SetVisAttributes(epoxy_va);
}

