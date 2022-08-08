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
/// \file optical/Sim/include/SimMainVolume.hh
/// \brief Definition of the SimMainVolume class
//
#ifndef SimBKF12_H
#define SimBKF12_H 1

#include "G4PVPlacement.hh"
#include "G4Box.hh"
#include "G4Tubs.hh"
#include "G4Material.hh"
#include "G4LogicalVolume.hh"
#include "G4OpticalSurface.hh"

#include "SimDetectorConstruction.hh"

class SimBKF12 : public G4PVPlacement
{
  public:

    SimBKF12(G4RotationMatrix *pRot,
                 const G4ThreeVector &tlate,
                 G4LogicalVolume *pMotherLogical,
                 G4bool pMany,
                 G4int pCopyNo,
                 SimDetectorConstruction* c);

  private:

    void VisAttributes();



    void CopyValues();

    SimDetectorConstruction* fConstructor;

    G4double fScint_x;
    G4double fScint_y;
    G4double fScint_z;
    G4double fD_mtl;
    G4int fNx;
    G4int fNy;
    G4int fNz;
    G4double fOuterRadius_pmt;
    G4double fRefl;

    G4double Space_Top;
    G4double Space_Down;
    G4double epoxy_size_x;
    G4double epoxy_size_y;
    G4double epoxy_size_z;
    G4double aluminium_size_x;
    G4double aluminium_size_y;
    G4double aluminium_size_z;
    G4double detector_size_z;

    //Basic Volumes
    //
    G4VSolid* fScint_box;
    G4VSolid* fHousing_box;
    G4Box* fPmt;
    G4Box* fPhotocath;
    G4Box* fAntiReflectivity;
    G4Box* epoxy_box;
    G4Box* aluminium_box;

    // Logical volumes
    //
    G4LogicalVolume* fScint_log;
    G4LogicalVolume* fHousing_log;
    G4LogicalVolume* fPmt_log;
    G4LogicalVolume* fPhotocath_log;
    G4LogicalVolume* fAntiReflectivity_log;
    G4LogicalVolume* epoxy_log;
    G4LogicalVolume* aluminium_log;


};

#endif
