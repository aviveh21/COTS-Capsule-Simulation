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
/// \file optical/Sim/src/SimRun.cc
/// \brief Implementation of the SimRun class
//
//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......
//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

#include "SimRun.hh"
#include "G4SystemOfUnits.hh"
#include <iostream>
#include <fstream>
#include <memory>
#include "FilePrinter.hh"

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......
SimRun::SimRun() : G4Run()
{
  fHitCount                = fHitCount2                = 0;
  fPhotonCount_Scint       = fPhotonCount_Scint2       = 0;
  fPhotonCount_Ceren       = fPhotonCount_Ceren2       = 0;
  fAbsorptionCount         = fAbsorptionCount2         = 0;
  fBoundaryAbsorptionCount = fBoundaryAbsorptionCount2 = 0;
  fPMTsAboveThreshold      = fPMTsAboveThreshold2      = 0;
  fSilicon1eCounter = 0;
  fSilicon2eCounter = 0;

  PMT.resize(NUM_OF_PMTS);

  fTotE = fTotE2 = 0.0;
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

SimRun::~SimRun()
{}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimRun::Merge(const G4Run* run)
{
  const SimRun* localRun = static_cast<const SimRun*>(run);

  fHitCount                 += localRun->fHitCount;
  fHitCount2                += localRun->fHitCount2;
  fPMTsAboveThreshold       += localRun->fPMTsAboveThreshold;
  fPMTsAboveThreshold2      += localRun->fPMTsAboveThreshold2;
  fPhotonCount_Scint        += localRun->fPhotonCount_Scint;
  fPhotonCount_Scint2       += localRun->fPhotonCount_Scint2;
  fPhotonCount_Ceren        += localRun->fPhotonCount_Ceren;
  fPhotonCount_Ceren2       += localRun->fPhotonCount_Ceren2;
  fAbsorptionCount          += localRun->fAbsorptionCount;
  fAbsorptionCount2         += localRun->fAbsorptionCount2;
  fBoundaryAbsorptionCount  += localRun->fBoundaryAbsorptionCount;
  fBoundaryAbsorptionCount2 += localRun->fBoundaryAbsorptionCount2;
  fTotE                     += localRun->fTotE;
  fTotE2                    += localRun->fTotE2;
  fSilicon1eCounter         += localRun->fSilicon1eCounter;
  fSilicon2eCounter         += localRun->fSilicon2eCounter;

  for (size_t i = 0; i < NUM_OF_PMTS; i++)
  {
         PMT[i] += localRun->PMT[i];
  }
  

  G4Run::Merge(run);
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SimRun::EndOfRun()
{
  static uint32_t a = 0;
  std::ofstream outFile(std::string("./output/") + std::to_string(a++) + std::string(".txt"));
  outFile << FilePrinter::GetStringAndReset();
  G4cout << "\n ======================== run summary ======================\n";

  G4int prec = G4cout.precision();

  G4int n_evt = numberOfEvent;
  G4cout << "The run was " << n_evt << " events." << G4endl;
 
  G4cout.precision(4);
  G4double hits = G4double(fHitCount)/n_evt;
  G4double hits2 = G4double(fHitCount2)/n_evt;
  G4double rms_hits = hits2 - hits*hits;
  if (rms_hits > 0.) rms_hits = std::sqrt(rms_hits/n_evt);
  else rms_hits = 0.;
  G4cout << "Number of hits per event:\t " << hits << " +- " << rms_hits 
         << G4endl;

  outFile << "Number of hits per event:\t " << hits << " +- " << rms_hits 
         << std::endl;

  G4double hitsAbove = G4double(fPMTsAboveThreshold)/n_evt;
  G4double hitsAbove2 = G4double(fPMTsAboveThreshold2)/n_evt;
  G4double rms_hitsAbove = hitsAbove2 - hitsAbove*hitsAbove;
  if (rms_hitsAbove > 0.) rms_hitsAbove = std::sqrt(rms_hitsAbove/n_evt);
  else rms_hitsAbove = 0.;

  G4cout << "Number of hits per event above threshold:\t " << hitsAbove 
         << " +- " << rms_hitsAbove << G4endl;

  outFile << "Number of hits per event above threshold:\t " << hitsAbove 
         << " +- " << rms_hitsAbove << std::endl;

  G4double scint = G4double(fPhotonCount_Scint)/n_evt;
  G4double scint2 = G4double(fPhotonCount_Scint2)/n_evt;
  G4double rms_scint = scint2 - scint*scint;
  if (rms_scint > 0.) rms_scint = std::sqrt(rms_scint/n_evt);
  else rms_scint = 0.;

  G4cout << "Number of scintillation photons per event :\t " << scint << " +- "
         << rms_scint << G4endl;
  outFile << "Number of scintillation photons per event :\t " << scint << " +- "
         << rms_scint << std::endl;

  G4double ceren = G4double(fPhotonCount_Ceren)/n_evt;
  G4double ceren2 = G4double(fPhotonCount_Ceren2)/n_evt;
  G4double rms_ceren = ceren2 - ceren*ceren;
  if (rms_ceren > 0.) rms_ceren = std::sqrt(rms_ceren/n_evt);
  else rms_ceren = 0.;

  G4cout << "Number of Cerenkov photons per event:\t " << ceren << " +- " 
         << rms_ceren << G4endl;

  G4double absorb = G4double(fAbsorptionCount)/n_evt;
  G4double absorb2 = G4double(fAbsorptionCount2)/n_evt;
  G4double rms_absorb = absorb2 - absorb*absorb;
  if (rms_absorb > 0.) rms_absorb = std::sqrt(rms_absorb/n_evt);
  else rms_absorb = 0.;

  G4cout << "Number of absorbed photons per event :\t " << absorb << " +- " 
         << rms_absorb << G4endl;
  outFile << "Number of absorbed photons per event :\t " << absorb << " +- " 
         << rms_absorb << std::endl;

  G4double bdry = G4double(fBoundaryAbsorptionCount)/n_evt;
  G4double bdry2 = G4double(fBoundaryAbsorptionCount2)/n_evt;
  G4double rms_bdry = bdry2 - bdry*bdry;
  if (rms_bdry > 0.) rms_bdry = std::sqrt(rms_bdry/n_evt);
  else rms_bdry = 0.;

  G4cout << "Number of photons absorbed at boundary per event:\t " << bdry 
         << " +- " << rms_bdry << G4endl;
  outFile << "Number of photons absorbed at boundary per event:\t " << bdry 
         << " +- " << rms_bdry << std::endl;
  //G4cout << "Number of unaccounted for photons: " << G4endl;

  G4double en = fTotE/n_evt;
  G4double en2 = fTotE2/n_evt;
  G4double rms_en = en2 - en*en;
  if (rms_en > 0.) rms_en = std::sqrt(rms_en/n_evt);
  else rms_en = 0.;

  G4cout << "Total energy deposition in scintillator per event:\t " << en/keV 
         << " +- " << rms_en/keV << " keV." << G4endl;
  outFile << "Total energy deposition in scintillator per event:\t " << en/keV 
         << " +- " << rms_en/keV << " keV." << std::endl;

  G4cout << "Silicon slab no. 1 electron count: "
         << fSilicon1eCounter << G4endl;
  G4cout << "Silicon slab no. 2 electron count: "
         << fSilicon2eCounter << G4endl;

  outFile << "Silicon slab no. 1 electron count: "
         << fSilicon1eCounter << std::endl;
  outFile << "Silicon slab no. 2 electron count: "
         << fSilicon2eCounter << std::endl;

  {
         std::vector<G4String> scint_loc;
         scint_loc.resize(4);
         scint_loc[0] = "Top-Right";
         scint_loc[1] = "Top-Left";
         scint_loc[2] = "Bottom-Left";
         scint_loc[3] = "Bottom-Right";
         for (size_t i = 0; i < NUM_OF_PMTS; i++)
         {
                outFile << "Scintillator " << (i / 4) + 1 << ", PMT " << i << " (" << scint_loc[i % 4] << "): " << PMT[i] << std::endl;
         }
  }

  G4cout << G4endl;
  G4cout.precision(prec);
}
