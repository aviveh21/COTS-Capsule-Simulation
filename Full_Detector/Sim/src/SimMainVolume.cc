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
/// \file optical/Sim/src/SimMainVolume.cc
/// \brief Implementation of the SimMainVolume class
//
//
#include "globals.hh"

#include "SimMainVolume.hh"

#include "G4LogicalSkinSurface.hh"
#include "G4LogicalBorderSurface.hh"

#include "G4SystemOfUnits.hh"
#include "G4SubtractionSolid.hh"

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

SimMainVolume::SimMainVolume(G4RotationMatrix *pRot,
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
  G4double housing_z=fScint_z+2.*fD_mtl;
 
  //*************************** housing and scintillator
  G4double dist_from_corner = fScint_z / 2;
  fScint_box = new G4Box("scint_box_removal", fScint_x / 2., fScint_y / 2., fScint_z / 2.);
  //*************************** housing and scintillator
  {
    std::vector<G4ThreeVector> cornerLocations;
    G4double x_loc = fScint_x / 2.; // - (sqrt(2) * dist_from_corner);
    G4double y_loc = fScint_y / 2.; // - (sqrt(2) * dist_from_corner);
    cornerLocations.emplace_back(x_loc, y_loc, 0);
    cornerLocations.emplace_back(x_loc, -y_loc, 0);
    cornerLocations.emplace_back(-x_loc, y_loc, 0);
    cornerLocations.emplace_back(-x_loc, -y_loc, 0);
    for (size_t i = 0; i < 4; i++)
    {

      G4VSolid *fCornerRemoval = new G4Box("scint_box_removal" + std::to_string(i), dist_from_corner, dist_from_corner, fScint_z);

      G4RotationMatrix *removal = new G4RotationMatrix();
      removal->rotateZ(45 * deg);
      std::string name = i == 3 ? "scint_box" : "scint_box" + std::to_string(i);
      fScint_box = new G4SubtractionSolid(name,                // name
                                          fScint_box,          // solid A
                                          fCornerRemoval,      // solid B
                                          removal,             // rotation
                                          cornerLocations[i]); // translation
    }
  }

  fHousing_box = new G4Box("housing_box_start", housing_x / 2., housing_y / 2., housing_z / 2.);
  G4double housing_dist_from_corner = dist_from_corner - fD_mtl;

  {
    // merge with last one
    std::vector<G4ThreeVector> cornerLocations;
    G4double x_loc = fScint_x / 2.;
    G4double y_loc = fScint_y / 2.;
    cornerLocations.emplace_back(x_loc, y_loc, 0);
    cornerLocations.emplace_back(x_loc, -y_loc, 0);
    cornerLocations.emplace_back(-x_loc, y_loc, 0);
    cornerLocations.emplace_back(-x_loc, -y_loc, 0);
    for (size_t i = 0; i < 4; i++)
    {
      G4double x_scale = cornerLocations[i].getX() * cornerLocations[i].getY() > 0 ? 2. : 1.;
      G4double y_scale = 3. - x_scale;
      G4VSolid *fCornerRemoval = new G4Box("housing_box_removal" + std::to_string(i), housing_dist_from_corner * x_scale, housing_dist_from_corner * y_scale, housing_z);

      G4RotationMatrix *removal = new G4RotationMatrix();
      removal->rotateZ(45 * deg);
      std::string name = i == 3 ? "housing_box" : "housing_box" + std::to_string(i);
      fHousing_box = new G4SubtractionSolid("housing_box" + std::to_string(i), // name
                                            fHousing_box,                      // solid A
                                            fCornerRemoval,                    // solid B
                                            removal,                           // rotation
                                            cornerLocations[i]);               // translation
    }
  }

  fScint_log = new G4LogicalVolume(fScint_box,G4Material::GetMaterial("Ej200"),
                                   "scint_log",0,0,0);
  fHousing_log = new G4LogicalVolume(fHousing_box,
                                     G4Material::GetMaterial("Air"),
                                     "housing_log",0,0,0);
 
  new G4PVPlacement(0,G4ThreeVector(),fScint_log,"scintillator",
                                 fHousing_log,false,0);

  //****************** Build PMTs
  G4double height_pmt = fD_mtl / 2.;

  G4double distFromCorner = (dist_from_corner / 2.) - 0.5 * height_pmt;
  G4double pmt_width = dist_from_corner;

  fPmt = new G4Box("pmt_box", pmt_width, (fScint_z) / 2.,
                   height_pmt);

  //the "photocathode" is a metal slab at the back of the glass that
  //is only a very rough approximation of the real thing since it only
  //absorbs or detects the photons based on the efficiency set below
  //
  fPhotocath = new G4Box("photocath_box", pmt_width, (fScint_z) / 2.,
                         height_pmt / 2.);

  fPmt_log = new G4LogicalVolume(fPmt, G4Material::GetMaterial("Glass"),
                                 "pmt_log");
  fPhotocath_log = new G4LogicalVolume(fPhotocath,
                                       G4Material::GetMaterial("Al"),
                                       "photocath_log");

  new G4PVPlacement(0, G4ThreeVector(0, 0, -height_pmt / 2),
                    fPhotocath_log, "photocath",
                    fPmt_log, false, 0);

  //***********Arrange pmts around the outside of housing**********

  static G4int k = 0;

  G4RotationMatrix *rm;
  G4ThreeVector offset;
  // G4ThreeVector loc;

  rm = new G4RotationMatrix(); // far right
  rm->rotateX(90 * deg);
  // rm->rotateY(135 * deg);
  rm->rotateY((135 + 0) * deg);
  offset = G4ThreeVector(-(sqrt(2) * (distFromCorner)), -(sqrt(2) * (distFromCorner)), 0);
  new G4PVPlacement(rm, G4ThreeVector(fScint_x / 2., fScint_y / 2., 0) + offset, fPmt_log, "pmt",
                    fHousing_log, false, k++);
  fPmtPositions.push_back(G4ThreeVector(fScint_x / 2., fScint_y / 2., 0) + offset);

  rm = new G4RotationMatrix(); // far left
  rm->rotateX(90 * deg);
  // rm->rotateY(225 * deg);
  rm->rotateY((225 + 0) * deg);
  offset = G4ThreeVector(-(sqrt(2) * (distFromCorner)), (sqrt(2) * (distFromCorner)), 0);
  new G4PVPlacement(rm, G4ThreeVector(fScint_x / 2., -fScint_y / 2., 0) + offset, fPmt_log, "pmt",
                    fHousing_log, false, k++);
  fPmtPositions.push_back(G4ThreeVector(fScint_x / 2., -fScint_y / 2., 0) + offset);

  rm = new G4RotationMatrix(); // close right
  rm->rotateX(90 * deg);
  // rm->rotateY(315 * deg);
  rm->rotateY((315 + 0) * deg);
  offset = G4ThreeVector((sqrt(2) * (distFromCorner)), (sqrt(2) * (distFromCorner)), 0);
  new G4PVPlacement(rm, G4ThreeVector(-fScint_x / 2, -fScint_y / 2., 0) + offset, fPmt_log, "pmt",
                    fHousing_log, false, k++);
  fPmtPositions.push_back(G4ThreeVector(-fScint_x / 2, -fScint_y / 2., 0) + offset);

  rm = new G4RotationMatrix(); // close left
  rm->rotateX(90 * deg);
  // rm->rotateY(45 * deg);
  rm->rotateY((45 + 0) * deg);
  offset = G4ThreeVector((sqrt(2) * (distFromCorner)), -(sqrt(2) * (distFromCorner)), 0);
  new G4PVPlacement(rm, G4ThreeVector(-fScint_x / 2, fScint_y / 2., 0) + offset, fPmt_log, "pmt",
                    fHousing_log, false, k++);
  fPmtPositions.push_back(G4ThreeVector(-fScint_x / 2, fScint_y / 2., 0) + offset);

  fNx = 2;
  fNy = 1;
  fNz = 0; // trick SD to recognize 4 pmts

  fAntiReflectivity = new G4Box("antiref_box", (fScint_y - ((dist_from_corner * 2) * sqrt(2.))) / 2., (fScint_z) / 2.,
                                height_pmt);

  fAntiReflectivity_log = new G4LogicalVolume(fAntiReflectivity, G4Material::GetMaterial("Al"),
                                              "antiref_log");

                                            
  rm = new G4RotationMatrix();
  rm->rotateX(90 * deg);
  new G4PVPlacement(rm, G4ThreeVector(0, fScint_y/2 + (height_pmt),  0), fAntiReflectivity_log, "antiref",
                    fHousing_log, false, 0);
  rm = new G4RotationMatrix();
  rm->rotateX(90 * deg);
  rm->rotateY(180 * deg);
  new G4PVPlacement(rm, G4ThreeVector(0, (fScint_y / 2 + (height_pmt))*-1, 0), fAntiReflectivity_log, "antiref",
                    fHousing_log, false, 1);
  rm = new G4RotationMatrix();
  rm->rotateX(90 * deg);
  rm->rotateY(90 * deg);
  new G4PVPlacement(rm, G4ThreeVector(fScint_y / 2 + (height_pmt), 0, 0), fAntiReflectivity_log, "antiref",
                    fHousing_log, false, 2);
  rm = new G4RotationMatrix();
  rm->rotateX(90 * deg);
  rm->rotateY(270 * deg);
  new G4PVPlacement(rm, G4ThreeVector((fScint_y / 2 + (height_pmt))*-1, 0, 0), fAntiReflectivity_log, "antiref",
                    fHousing_log, false, 3);

  VisAttributes();
  SurfaceProperties();

  SetLogicalVolume(fHousing_log);
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimMainVolume::CopyValues(){
  fScint_x=fConstructor->GetScintX();
  fScint_y=fConstructor->GetScintY();
  fScint_z=fConstructor->GetScintZ();
  fD_mtl=fConstructor->GetHousingThickness();
  fNx=fConstructor->GetNX();
  fNy=fConstructor->GetNY();
  fNz=fConstructor->GetNZ();
  fOuterRadius_pmt=fConstructor->GetPMTRadius();
  fRefl=fConstructor->GetHousingReflectivity();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimMainVolume::PlacePMTs(G4LogicalVolume* pmt_log,
                              G4RotationMatrix *rot,
                              G4double &a, G4double &b, G4double da,
                              G4double db, G4double amin,
                              G4double bmin, G4int na, G4int nb,
                              G4double &x, G4double &y, G4double &z,
                              G4int &k){
/*PlacePMTs : a different way to parameterize placement that does not depend on
  calculating the position from the copy number

  pmt_log = logical volume for pmts to be placed
  rot = rotation matrix to apply
  a,b = coordinates to vary(ie. if varying in the xy plane then pass x,y)
  da,db = value to increment a,b by
  amin,bmin = start values for a,b
  na,nb = number of repitions in a and b
  x,y,z = just pass x,y, and z by reference (the same ones passed for a,b)
  k = copy number to start with
  sd = sensitive detector for pmts
*/
  a=amin;
  for(G4int j=1;j<=na;j++){
    a+=da;
    b=bmin;
    for(G4int i=1;i<=nb;i++){
      b+=db;
      new G4PVPlacement(rot,G4ThreeVector(x,y,z),pmt_log,"pmt",
                        fHousing_log,false,k);
      fPmtPositions.push_back(G4ThreeVector(x,y,z));
      k++;
    }
  }
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimMainVolume::VisAttributes(){
  G4VisAttributes* housing_va = new G4VisAttributes(G4Colour(0.8,0.8,0.8));
  fHousing_log->SetVisAttributes(housing_va);
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimMainVolume::SurfaceProperties(){
  G4double ephoton[] = {7.0*eV, 7.14*eV};
  const G4int num = sizeof(ephoton)/sizeof(G4double);

  //**Scintillator housing properties
  G4double reflectivity[] = {1., 1.};
  assert(sizeof(reflectivity) == sizeof(ephoton));
  G4double efficiency[] = {0.0, 0.0};
  assert(sizeof(efficiency) == sizeof(ephoton));
  G4MaterialPropertiesTable* scintHsngPT = new G4MaterialPropertiesTable();
  scintHsngPT->AddProperty("REFLECTIVITY", ephoton, reflectivity, num);
  scintHsngPT->AddProperty("EFFICIENCY", ephoton, efficiency, num);
  G4OpticalSurface* OpScintHousingSurface =
    new G4OpticalSurface("HousingSurface",unified,polished,dielectric_metal);
  OpScintHousingSurface->SetMaterialPropertiesTable(scintHsngPT);
  OpScintHousingSurface->SetPolish(0.);
 
  //**Photocathode surface properties
  G4double photocath_EFF[]={1.,1.}; //Enables 'detection' of photons
  assert(sizeof(photocath_EFF) == sizeof(ephoton));
  G4double photocath_ReR[]={1.92,1.92};
  assert(sizeof(photocath_ReR) == sizeof(ephoton));
  G4double photocath_ImR[]={1.69,1.69};
  assert(sizeof(photocath_ImR) == sizeof(ephoton));
  G4double photocath_Reflectivity[]={0.,0.};
  assert(sizeof(photocath_Reflectivity) == sizeof(ephoton));
  G4MaterialPropertiesTable* photocath_mt = new G4MaterialPropertiesTable();
  photocath_mt->AddProperty("EFFICIENCY",ephoton,photocath_EFF,num);
  photocath_mt->AddProperty("REALRINDEX",ephoton,photocath_ReR,num);
  photocath_mt->AddProperty("IMAGINARYRINDEX",ephoton,photocath_ImR,num);
  photocath_mt->AddProperty("REFLECTIVITY", ephoton, photocath_Reflectivity, num);
  G4OpticalSurface* photocath_opsurf=
    new G4OpticalSurface("photocath_opsurf",glisur,polished,
                         dielectric_metal);
  photocath_opsurf->SetMaterialPropertiesTable(photocath_mt);

  G4double ar_reflectivity[] = {0., 0.};
  assert(sizeof(ar_reflectivity) == sizeof(ephoton));
  G4double ar_efficiency[] = {0.0, 0.0};
  assert(sizeof(ar_efficiency) == sizeof(ephoton));
  G4MaterialPropertiesTable* antiRef_PT = new G4MaterialPropertiesTable();
  antiRef_PT->AddProperty("REFLECTIVITY", ephoton, ar_reflectivity, num);
  antiRef_PT->AddProperty("EFFICIENCY", ephoton, ar_efficiency, num);
  G4OpticalSurface *antiRef_Surface =
      new G4OpticalSurface("antiRefSurface", glisur, polished, dielectric_metal);
  antiRef_Surface->SetMaterialPropertiesTable(antiRef_PT);
  // antiRef_Surface->SetPolish(1.);

  //**Create logical skin surfaces
  new G4LogicalSkinSurface("photocath_surf",fHousing_log,
                           OpScintHousingSurface);
  new G4LogicalSkinSurface("photocath_surf",fPhotocath_log,photocath_opsurf);
  new G4LogicalSkinSurface("antiref_surf",fAntiReflectivity_log,antiRef_Surface);
}
