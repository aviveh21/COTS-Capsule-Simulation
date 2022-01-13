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
/// \file optical/Sim/include/SimScintHit.hh
/// \brief Definition of the SimScintHit class
//
//
#ifndef SimScintHit_h
#define SimScintHit_h 1

#include "G4VHit.hh"
#include "G4THitsCollection.hh"
#include "G4Allocator.hh"
#include "G4ThreeVector.hh"
#include "G4LogicalVolume.hh"
#include "G4Transform3D.hh"
#include "G4RotationMatrix.hh"
#include "G4VPhysicalVolume.hh"

#include "tls.hh"

class SimScintHit : public G4VHit
{
  public:
 
    SimScintHit();
    SimScintHit(G4VPhysicalVolume* pVol);
    virtual ~SimScintHit();
    SimScintHit(const SimScintHit &right);
    const SimScintHit& operator=(const SimScintHit &right);
    G4bool operator==(const SimScintHit &right) const;

    inline void *operator new(size_t);
    inline void operator delete(void *aHit);
 
    virtual void Draw();
    virtual void Print();

    inline void SetEdep(G4double de) { fEdep = de; }
    inline void AddEdep(G4double de) { fEdep += de; }
    inline G4double GetEdep() { return fEdep; }

    inline void SetPos(G4ThreeVector xyz) { fPos = xyz; }
    inline G4ThreeVector GetPos() { return fPos; }

    inline const G4VPhysicalVolume * GetPhysV() { return fPhysVol; }

  private:
    G4double fEdep;
    G4ThreeVector fPos;
    const G4VPhysicalVolume* fPhysVol;

};

typedef G4THitsCollection<SimScintHit> SimScintHitsCollection;

extern G4ThreadLocal G4Allocator<SimScintHit>* SimScintHitAllocator;

inline void* SimScintHit::operator new(size_t)
{
  if(!SimScintHitAllocator)
      SimScintHitAllocator = new G4Allocator<SimScintHit>;
  return (void *) SimScintHitAllocator->MallocSingle();
}

inline void SimScintHit::operator delete(void *aHit)
{
  SimScintHitAllocator->FreeSingle((SimScintHit*) aHit);
}

#endif
