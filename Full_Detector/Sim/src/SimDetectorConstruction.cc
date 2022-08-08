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
/// \file optical/Sim/src/SimDetectorConstruction.cc
/// \brief Implementation of the SimDetectorConstruction class
//
//
#include "SimDetectorConstruction.hh"
#include "SimPMTSD.hh"
#include "SimScintSD.hh"
#include "SimDetectorMessenger.hh"
#include "SimMainVolume.hh"
#include "SimBKF12.hh"
#include "SimRun.hh"
#include "G4SDManager.hh"
#include "G4RunManager.hh"

#include "G4GeometryManager.hh"
#include "G4SolidStore.hh"
#include "G4LogicalVolumeStore.hh"
#include "G4PhysicalVolumeStore.hh"
#include "G4LogicalBorderSurface.hh"
#include "G4LogicalSkinSurface.hh"

#include "G4OpticalSurface.hh"
#include "G4MaterialTable.hh"
#include "G4VisAttributes.hh"
#include "G4Material.hh"
#include "G4Box.hh"
#include "G4Tubs.hh"
#include "G4LogicalVolume.hh"
#include "G4ThreeVector.hh"
#include "G4PVPlacement.hh"
#include "globals.hh"
#include "G4UImanager.hh"
#include "G4PhysicalConstants.hh"
#include "G4SystemOfUnits.hh"

#include "SD.hh"
#include "G4ProductionCuts.hh"


//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

SimDetectorConstruction::SimDetectorConstruction()
: fSim_mt(nullptr), fMPTPStyrene(nullptr)
{
  fExperimentalHall_box = nullptr;
  fExperimentalHall_log = nullptr;
  fExperimentalHall_phys = nullptr;

  fSim = fAl = fAir = fVacuum = fGlass = nullptr;
  fPstyrene = fPMMA = fPethylene1 = fPethylene2 = nullptr;

  fN = fO = fC = fH = nullptr;

  fSaveThreshold = 0;
  SetDefaults();

  DefineMaterials();
  fDetectorMessenger = new SimDetectorMessenger(this);
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

SimDetectorConstruction::~SimDetectorConstruction() {}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimDetectorConstruction::DefineMaterials(){
  G4double a;  // atomic mass
  G4double z;  // atomic number
  G4double density;

  G4int polyPMMA = 1;
  G4int nC_PMMA = 3+2*polyPMMA;
  G4int nH_PMMA = 6+2*polyPMMA;

  G4int polyeth = 1;
  G4int nC_eth = 2*polyeth;
  G4int nH_eth = 4*polyeth;

  //***Elements
  fH = new G4Element("H", "H", z=1., a=1.01*g/mole);
  fC = new G4Element("C", "C", z=6., a=12.01*g/mole);
  fN = new G4Element("N", "N", z=7., a= 14.01*g/mole);
  fO = new G4Element("O"  , "O", z=8., a= 16.00*g/mole);

  //***Materials
  //Liquid Xenon
  fSim = new G4Material("Sim",z=54.,a=131.29*g/mole,density=3.020*g/cm3);
  //Aluminum
  fAl = new G4Material("Al",z=13.,a=26.98*g/mole,density=2.7*g/cm3);
  //Vacuum
  fVacuum = new G4Material("Vacuum",z=1.,a=1.01*g/mole,
                          density=universe_mean_density,kStateGas,0.1*kelvin,
                          1.e-19*pascal);
  //Air
  fAir = new G4Material("Air", density= 1.29*mg/cm3, 2);
  fAir->AddElement(fN, 70*perCent);
  fAir->AddElement(fO, 30*perCent);
  //Glass
  fGlass = new G4Material("Glass", density=1.032*g/cm3,2);
  fGlass->AddElement(fC,91.533*perCent);
  fGlass->AddElement(fH,8.467*perCent);
  //Polystyrene
  fPstyrene = new G4Material("Polystyrene", density= 1.03*g/cm3, 2);
  fPstyrene->AddElement(fC, 8);
  fPstyrene->AddElement(fH, 8);
  //Fiber(PMMA)
  fPMMA = new G4Material("PMMA", density=1190*kg/m3,3);
  fPMMA->AddElement(fH,nH_PMMA);
  fPMMA->AddElement(fC,nC_PMMA);
  fPMMA->AddElement(fO,2);
  //Cladding(polyethylene)
  fPethylene1 = new G4Material("Pethylene1", density=1200*kg/m3,2);
  fPethylene1->AddElement(fH,nH_eth);
  fPethylene1->AddElement(fC,nC_eth);
  //Double cladding(flourinated polyethylene)
  fPethylene2 = new G4Material("Pethylene2", density=1400*kg/m3,2);
  fPethylene2->AddElement(fH,nH_eth);
  fPethylene2->AddElement(fC,nC_eth);

  Ej200 = new G4Material("Ej200", density = 1.023 * g / cm3, 2);
  Ej200->AddElement(fC, 9);
  Ej200->AddElement(fH, 10);

  //Epoxy (for the cover of each detector)

  //Epoxy (for FR4 )
  //G4Material* Epoxy = new G4Material("Epoxy" , density = 1.2*g/cm3, 2);
  //Epoxy->AddElement(fH, 2);
  //Epoxy->AddElement(fC, 2);

  //another option
  Epoxy = new G4Material("Epoxy",  density = 1.16*g/cm3, 4);
  Epoxy->AddElement(fH, 32); // Hydrogen
  Epoxy->AddElement(fN,  2); // Nitrogen
  Epoxy->AddElement(fO,  4); // Oxygen
  Epoxy->AddElement(fC, 15); // Carbon

  

  //***Material properties tables
  const G4int NUMENTRIES = 12;
  G4double PhotonEnergy[NUMENTRIES] = {3.44 * eV, 3.26 * eV, 3.1 * eV, 3.02 * eV, 2.95 * eV,
                                       2.92 * eV, 2.82 * eV, 2.76 * eV, 2.7 * eV, 2.58 * eV,
                                       2.38 * eV, 2.08 * eV};
  G4double RINDEX_Ej200[NUMENTRIES] = {1.58, 1.58, 1.58, 1.58, 1.58,
                                       1.58, 1.58, 1.58, 1.58, 1.58,
                                       1.58, 1.58};
  G4double ABSORPTION_Ej200[NUMENTRIES] = {210 * cm, 210 * cm, 210 * cm, 210 * cm, 210 * cm,
                                           210 * cm, 210 * cm, 210 * cm, 210 * cm, 210 * cm,
                                           210 * cm, 210 * cm};
  G4double SCINTILLATION_Ej200[NUMENTRIES] = {0.04, 0.07, 0.20, 0.49, 0.84,
                                              1.00, 0.83, 0.55, 0.40, 0.17,
                                              0.03, 0};
  
  //Included for Epoxy
  G4double REFLECTIVENESS_Epoxy[NUMENTRIES] = {0.045, 0.045, 0.045, 0.045, 0.045,
                                              0.045, 0.045, 0.045, 0.045, 0.045,
                                              0.045, 0.045};
  G4double RINDEX_Epoxy[NUMENTRIES] = {1.5, 1.5, 1.5, 1.5, 1.5,
                                       1.5, 1.5, 1.5, 1.5, 1.5,
                                       1.5, 1.5};
  Epoxy_mt = new G4MaterialPropertiesTable();
  Epoxy_mt->AddProperty("REFLECTIVITY",  PhotonEnergy, REFLECTIVENESS_Epoxy, NUMENTRIES);
  Epoxy_mt->AddProperty("RINDEX", PhotonEnergy, RINDEX_Epoxy, NUMENTRIES);
  Epoxy->SetMaterialPropertiesTable(Epoxy_mt);

  //For EJ200
  Ej200_mt = new G4MaterialPropertiesTable();
  Ej200_mt->AddProperty("RINDEX", PhotonEnergy, RINDEX_Ej200, NUMENTRIES);
  Ej200_mt->AddProperty("ABSLENGTH", PhotonEnergy, ABSORPTION_Ej200, NUMENTRIES);
  Ej200_mt->AddProperty("FASTCOMPONENT", PhotonEnergy, SCINTILLATION_Ej200, NUMENTRIES);
  Ej200_mt->AddConstProperty("SCINTILLATIONYIELD", 10000. / MeV);
  Ej200_mt->AddConstProperty("RESOLUTIONSCALE", 1.0);
  Ej200_mt->AddConstProperty("FASTTIMECONSTANT", 1. * ns);
  // Ej200_mt->AddConstProperty("SLOWTIMECONSTANT",1.*ns);
  Ej200_mt->AddConstProperty("YIELDRATIO", 1.);
  Ej200->SetMaterialPropertiesTable(Ej200_mt);

  //***Material properties tables

  G4double sim_Energy[]    = { 7.0*eV , 7.07*eV, 7.14*eV };
  const G4int simnum = sizeof(sim_Energy)/sizeof(G4double);

  G4double sim_SCINT[] = { 0.1, 1.0, 0.1 };
  assert(sizeof(sim_SCINT) == sizeof(sim_Energy));
  G4double sim_RIND[]  = { 1.59 , 1.57, 1.54 };
  assert(sizeof(sim_RIND) == sizeof(sim_Energy));
  G4double sim_ABSL[]  = { 35.*cm, 35.*cm, 35.*cm};
  assert(sizeof(sim_ABSL) == sizeof(sim_Energy));
  fSim_mt = new G4MaterialPropertiesTable();
  fSim_mt->AddProperty("FASTCOMPONENT", sim_Energy, sim_SCINT, simnum);
  fSim_mt->AddProperty("SLOWCOMPONENT", sim_Energy, sim_SCINT, simnum);
  fSim_mt->AddProperty("RINDEX",        sim_Energy, sim_RIND,  simnum);
  fSim_mt->AddProperty("ABSLENGTH",     sim_Energy, sim_ABSL,  simnum);
  fSim_mt->AddConstProperty("SCINTILLATIONYIELD",12000./MeV);
  fSim_mt->AddConstProperty("RESOLUTIONSCALE",1.0);
  fSim_mt->AddConstProperty("FASTTIMECONSTANT",20.*ns);
  fSim_mt->AddConstProperty("SLOWTIMECONSTANT",45.*ns);
  fSim_mt->AddConstProperty("YIELDRATIO",1.0);
  fSim->SetMaterialPropertiesTable(fSim_mt);

  // Set the Birks Constant for the Sim scintillator

  fSim->GetIonisation()->SetBirksConstant(0.126*mm/MeV);
 
  G4double glass_RIND[]={1.49,1.49,1.49};
  assert(sizeof(glass_RIND) == sizeof(sim_Energy));
  G4double glass_AbsLength[]={420.*cm,420.*cm,420.*cm};
  assert(sizeof(glass_AbsLength) == sizeof(sim_Energy));
  G4MaterialPropertiesTable *glass_mt = new G4MaterialPropertiesTable();
  glass_mt->AddProperty("ABSLENGTH",sim_Energy,glass_AbsLength,simnum);
  glass_mt->AddProperty("RINDEX",sim_Energy,glass_RIND,simnum);
  fGlass->SetMaterialPropertiesTable(glass_mt);

  G4double vacuum_Energy[]={2.0*eV,7.0*eV,7.14*eV};
  const G4int vacnum = sizeof(vacuum_Energy)/sizeof(G4double);
  G4double vacuum_RIND[]={1.,1.,1.};
  assert(sizeof(vacuum_RIND) == sizeof(vacuum_Energy));
  G4MaterialPropertiesTable *vacuum_mt = new G4MaterialPropertiesTable();
  vacuum_mt->AddProperty("RINDEX", vacuum_Energy, vacuum_RIND,vacnum);
  fVacuum->SetMaterialPropertiesTable(vacuum_mt);
  fAir->SetMaterialPropertiesTable(vacuum_mt);//Give air the same rindex

  G4NistManager * man = G4NistManager::Instance();
  G4Material * Si = man->FindOrBuildMaterial("G4_Si");
  fSiMaterial = Si;
  G4NistManager * man_1 = G4NistManager::Instance();
  G4Material * Al = man_1->FindOrBuildMaterial("G4_Al");
  fAlMaterial = Al;
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

G4VPhysicalVolume* SimDetectorConstruction::Construct(){

  if (fExperimentalHall_phys) { return fExperimentalHall_phys; }

  //The experimental hall walls are all 1m away from housing walls

  G4double expHall_x = fScint_x+fD_mtl+1.*m;
  G4double expHall_y = fScint_y+fD_mtl+1.*m;
  G4double expHall_z = detector_size_z*5.+1.5*m;

  //Create experimental hall
  fExperimentalHall_box
    = new G4Box("expHall_box",expHall_x,expHall_y,expHall_z);
  fExperimentalHall_log = new G4LogicalVolume(fExperimentalHall_box,
                                             fVacuum,"expHall_log",0,0,0);
  fExperimentalHall_phys = new G4PVPlacement(0,G4ThreeVector(),
                              fExperimentalHall_log,"expHall",0,false,0);

  fExperimentalHall_log->SetVisAttributes(G4VisAttributes::GetInvisible());

  //Place the main volumes - scintillators!
  if(fMainVolumeOn){

    

    fMainVolume
      = new SimMainVolume(0,G4ThreeVector(),fExperimentalHall_log,false,0,this);
    //bkf_det1
    //  = new SimBKF12(0,G4ThreeVector(),fExperimentalHall_log,false,0,this );

    fMainVolume2 
      = new SimMainVolume(0, G4ThreeVector(0., 0., 1.0*detector_size_z), fExperimentalHall_log, false, 0, this);
    //bkf_det2
    //  = new SimBKF12(0,G4ThreeVector(0., 0., 1.0*detector_size_z),fExperimentalHall_log,false,0,this );

    fMainVolume3 
      = new SimMainVolume(0, G4ThreeVector(0., 0., 2.0*detector_size_z), fExperimentalHall_log, false, 0, this);
    //bkf_det3
    //  = new SimBKF12(0,G4ThreeVector(0., 0., 2.0*detector_size_z),fExperimentalHall_log,false,0,this );

    fMainVolume4 
      = new SimMainVolume(0, G4ThreeVector(0., 0., 3.0*detector_size_z), fExperimentalHall_log, false, 0, this);
    //bkf_det4
    //  = new SimBKF12(0,G4ThreeVector(0., 0., 3.0*detector_size_z),fExperimentalHall_log,false,0,this );

    fMainVolume5 
      = new SimMainVolume(0, G4ThreeVector(0., 0., 4.0*detector_size_z), fExperimentalHall_log, false, 0, this);
    //bkf_det5
    //  = new SimBKF12(0,G4ThreeVector(0., 0., 4.0*detector_size_z),fExperimentalHall_log,false,0,this );
    
  }

  //Place the silicon!
  //G4double TargetSizeZ = 0.3*mm;//0.2*um; 
  //G4double TargetSizeX = 63.*mm;
  //G4double TargetSizeY = 63.*mm;

  //G4Box* targetSolid = new G4Box("Silicon_1",				     //its name
	//			 TargetSizeX/2,TargetSizeY/2,TargetSizeZ/2);   //its size


  //G4LogicalVolume *logicTarget = new G4LogicalVolume(targetSolid, //its solid
  //                                                   fSiMaterial, //its material
  //                                                   "Target");   //its name

  //new G4PVPlacement(0,                                      //no rotation
  //                  vSilicon1Location, //at (0,0,0)
  //                  logicTarget,                            //its logical volume
  //                  "Target",
  //                  fExperimentalHall_log, //its mother  volume
  //                  0,
  //                  false, //no boolean operation
  //                  0);    //copy number

  // Visualization attributes
  //G4VisAttributes* worldVisAtt1 = new G4VisAttributes(G4Colour(1.0,0.0,0.0)); 
  //worldVisAtt1->SetVisibility(true);
  //logicTarget->SetVisAttributes(worldVisAtt1);

  //G4Box* targetSolid_2 = new G4Box("Silicon_2",				     //its name
	//			 TargetSizeX/2,TargetSizeY/2,TargetSizeZ/2);   //its size

  //G4LogicalVolume *logicTarget_2 = new G4LogicalVolume(targetSolid_2, //its solid
  //                                                    fSiMaterial, //its material
  //                                                    "Target");   //its name

  //new G4PVPlacement(0,                                      //no rotation
  //                  vSilicon2Location, //at (0,0,0)
  //                  logicTarget_2,                            //its logical volume
  //                  "Target",
  //                  fExperimentalHall_log, //its mother  volume
  //                  0,
  //                  false, //no boolean operation
  //                  0);    //copy number

  // Visualization attributes
  //worldVisAtt1 = new G4VisAttributes(G4Colour(1.0,0.0,0.0)); 
  //worldVisAtt1->SetVisibility(true);
  //logicTarget_2->SetVisAttributes(worldVisAtt1);


// Place the Aluminium Cover Up of the Entire Detector (1 On top, 1 On bottom)



  G4Box* AluminumSolid = new G4Box("Alcover_1",				     //its name
				 AlcoverSizeX/2,AlcoverSizeY/2,AlcoverSizeZ/2);   //its size


  G4LogicalVolume *logicAluminum_1 = new G4LogicalVolume(AluminumSolid, //its solid
                                                     fAlMaterial, //its material
                                                     "Alcover_1");   //its name

  new G4PVPlacement(0,                                      //no rotation
                    Alcover1Location, //at (0,0,0)
                    logicAluminum_1,                            //its logical volume
                    "Alcover_1",
                    fExperimentalHall_log, //its mother  volume
                    0,
                    false, //no boolean operation
                    0);    //copy number

  G4LogicalVolume *logicAluminum_2 = new G4LogicalVolume(AluminumSolid, //its solid
                                                     fAlMaterial, //its material
                                                     "Alcover_2");   //its name

  new G4PVPlacement(0,                                      //no rotation
                    Alcover2Location, //at (0,0,0)
                    logicAluminum_2,                            //its logical volume
                    "Alcover_2",
                    fExperimentalHall_log, //its mother  volume
                    0,
                    false, //no boolean operation
                    0);    //copy number

  // Visualization attributes
  G4VisAttributes* worldVisAtt1 = new G4VisAttributes(G4Colour(1.0,0.0,0.0)); 
  worldVisAtt1->SetVisibility(true);
  logicAluminum_1->SetVisAttributes(worldVisAtt1);
  logicAluminum_2->SetVisAttributes(worldVisAtt1);

  // Create Target G4Region and add logical volume
  
  fRegion = new G4Region("Target");
  
  G4ProductionCuts* cuts = new G4ProductionCuts();
  
  G4double defCut = 1*nanometer;
  cuts->SetProductionCut(defCut,"gamma");
  cuts->SetProductionCut(defCut,"e-");
  cuts->SetProductionCut(defCut,"e+");
  cuts->SetProductionCut(defCut,"proton");
  
  fRegion->SetProductionCuts(cuts);
  //fRegion->AddRootLogicalVolume(logicTarget); 
  //fRegion->AddRootLogicalVolume(logicTarget_2);

// 08/01/22 Aviv tried to put the tracker on the scintilators

  //fRegion->AddRootLogicalVolume(fMainVolume->GetLogScint());
  //fRegion->AddRootLogicalVolume(fMainVolume2->GetLogScint());
  //fRegion->AddRootLogicalVolume(fMainVolume3->GetLogScint());
  //fRegion->AddRootLogicalVolume(fMainVolume4->GetLogScint());
  //fRegion->AddRootLogicalVolume(fMainVolume5->GetLogScint());

  return fExperimentalHall_phys;
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimDetectorConstruction::ConstructSDandField() {

  if (!fMainVolume) return;

  // PMT SD

  if (!fPmt_SD.Get()) {
    //Created here so it exists as pmts are being placed
    G4cout << "Construction /SimDet/pmtSD" << G4endl;
    SimPMTSD* pmt_SD = new SimPMTSD("/SimDet/pmtSD");
    fPmt_SD.Put(pmt_SD);

    pmt_SD->InitPMTs(NUM_OF_PMTS); //let pmtSD know # of pmts
    std::vector<G4ThreeVector> total = fMainVolume->GetPmtPositions();
    auto a = fMainVolume2->GetPmtPositions();
    total.insert(total.end(), a.begin(), a.end());

//01/01/22 - Shalev told me to change this for the PMT position

    auto b = fMainVolume3->GetPmtPositions();
    total.insert(total.end(), b.begin(), b.end());
    auto c = fMainVolume4->GetPmtPositions();
    total.insert(total.end(), c.begin(), c.end());
    auto d = fMainVolume5->GetPmtPositions();
    total.insert(total.end(), d.begin(), d.end());

// 08/01/22 "total" is a maarach with all the positions of tne PMTs for every scintilator

    pmt_SD->SetPmtPositions(total);
  }
  G4SDManager::GetSDMpointer()->AddNewDetector(fPmt_SD.Get());
  //sensitive detector is not actually on the photocathode.
  //processHits gets done manually by the stepping action.
  //It is used to detect when photons hit and get absorbed&detected at the
  //boundary to the photocathode (which doesnt get done by attaching it to a
  //logical volume.
  //It does however need to be attached to something or else it doesnt get
  //reset at the begining of events

  SetSensitiveDetector(fMainVolume->GetLogPhotoCath(), fPmt_SD.Get());
  SetSensitiveDetector(fMainVolume2->GetLogPhotoCath(), fPmt_SD.Get());
  SetSensitiveDetector(fMainVolume3->GetLogPhotoCath(), fPmt_SD.Get());
  SetSensitiveDetector(fMainVolume4->GetLogPhotoCath(), fPmt_SD.Get());
  SetSensitiveDetector(fMainVolume5->GetLogPhotoCath(), fPmt_SD.Get());
  // Scint SD

  if (!fScint_SD.Get()) {
    G4cout << "Construction /SimDet/scintSD" << G4endl;
    SimScintSD* scint_SD = new SimScintSD("/SimDet/scintSD");
    fScint_SD.Put(scint_SD);
  }
  G4SDManager::GetSDMpointer()->AddNewDetector(fScint_SD.Get());
  SetSensitiveDetector("scint_log", fScint_SD.Get(), true);

  //G4String trackerChamberSDname = "B2/TrackerChamberSD";
  //B2TrackerSD* aTrackerSD = new B2TrackerSD(trackerChamberSDname,
  //                                          "TrackerHitsCollection");
  //G4SDManager::GetSDMpointer()->AddNewDetector(aTrackerSD);
  // Setting aTrackerSD to all logical volumes with the same name 
  // of "Chamber_LV".
  //SetSensitiveDetector("Target", aTrackerSD, true);
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimDetectorConstruction::SetDimensions(G4ThreeVector dims) {
  fScint_x=dims[0];
  fScint_y=dims[1];
  fScint_z=dims[2];
  G4RunManager::GetRunManager()->ReinitializeGeometry();
}
 
//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimDetectorConstruction::SetHousingThickness(G4double d_mtl) {
  fD_mtl=d_mtl;
  G4RunManager::GetRunManager()->ReinitializeGeometry();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimDetectorConstruction::SetNX(G4int nx) {
  fNx=nx;
  G4RunManager::GetRunManager()->ReinitializeGeometry();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimDetectorConstruction::SetNY(G4int ny) {
  fNy=ny;
  G4RunManager::GetRunManager()->ReinitializeGeometry();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimDetectorConstruction::SetNZ(G4int nz) {
  fNz=nz;
  G4RunManager::GetRunManager()->ReinitializeGeometry();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimDetectorConstruction::SetPMTRadius(G4double outerRadius_pmt) {
  fOuterRadius_pmt=outerRadius_pmt;
  G4RunManager::GetRunManager()->ReinitializeGeometry();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimDetectorConstruction::SetDefaults() {

  //Resets to default values
  fD_mtl=0.023188*cm;

  //Scintilator
  fScint_x = 7.*cm;
  fScint_y = 7.*cm;
  fScint_z = 0.67*cm;
  
  //BKF12
  epoxy_size_x= fScint_x;
  epoxy_size_y= fScint_y;
  epoxy_size_z= 0.001*cm;
  aluminium_size_x=fScint_x;
  aluminium_size_y=fScint_y;
  aluminium_size_z=0.005*cm;
  BKF12_size_z=epoxy_size_z*2.+aluminium_size_z;
  

  AlcoverSizeZ = 0.08*cm;//0.2*um; 
  AlcoverSizeX = 7.*cm;
  AlcoverSizeY = 7.*cm;
  Space_Top=0.36*cm; // In a detector - Space between Scintilator to the BKF and Apoxy at the Top 
  Space_Down=0.17*cm; // In a detector - Space between Scintilator to the BKF and Apoxy at the Bottom 
  
  //Full Detector
  detector_size_z=fScint_z +Space_Down+Space_Top+BKF12_size_z*2.; // 1.214 cm

  fNx = 2;
  fNy = 1;
  fNz = 0;

  fOuterRadius_pmt = 2.3*cm;

  fRefl = 1.0;

  fNfibers = 15;
  fMainVolumeOn = true;
  fMainVolume = nullptr;
  fSlab_z = 2.5*mm;
  
  Alcover1Location = G4ThreeVector(0., 0., ((Space_Top-Space_Down)/2.-fScint_z/2-AlcoverSizeZ/2.-BKF12_size_z-Space_Top)); // Z= -0.647cm // before the first Scintilator, including the apoxy and BKF12, the 0.004 is to put the alcover exectly after the Scintilator
  Alcover2Location = G4ThreeVector(0., 0., ((Space_Top-Space_Down)/2.+4*detector_size_z+fScint_z/2+AlcoverSizeZ/2.+BKF12_size_z+Space_Down)); // Z= 5.503cm // After the last Scintilator, including the apoxy and BKF12, the 0.004 is to put the alcover exectly after the Scintilator

  vSilicon1Location = G4ThreeVector(0., 0., -0.64 * 2. * cm);
  vSilicon2Location = G4ThreeVector(0., 0., -0.64 * 4. * cm);

  G4UImanager::GetUIpointer()
    ->ApplyCommand("/Sim/detector/scintYieldFactor 1.");

  if(fSim_mt)fSim_mt->AddConstProperty("SCINTILLATIONYIELD",12000./MeV);
  if(fMPTPStyrene)fMPTPStyrene->AddConstProperty("SCINTILLATIONYIELD",10./keV);

}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimDetectorConstruction::SetHousingReflectivity(G4double r) {
  fRefl=r;
  G4RunManager::GetRunManager()->ReinitializeGeometry();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimDetectorConstruction::SetMainVolumeOn(G4bool b) {
  fMainVolumeOn=b;
  G4RunManager::GetRunManager()->ReinitializeGeometry();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimDetectorConstruction::SetNFibers(G4int n) {
  fNfibers=n;
  G4RunManager::GetRunManager()->ReinitializeGeometry();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimDetectorConstruction::SetMainScintYield(G4double y) {
  fSim_mt->AddConstProperty("SCINTILLATIONYIELD",y/MeV);
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimDetectorConstruction::SetSaveThreshold(G4int save){
/*Sets the save threshold for the random number seed. If the number of photons
generated in an event is lower than this, then save the seed for this event
in a file called run###evt###.rndm
*/
  fSaveThreshold=save;
  G4RunManager::GetRunManager()->SetRandomNumberStore(true);
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......
