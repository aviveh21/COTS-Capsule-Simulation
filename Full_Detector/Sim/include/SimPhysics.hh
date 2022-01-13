#ifndef SimPhysics_h
#define SimPhysics_h 1

#include "G4EmStandardPhysics_option4.hh"

class SimPhysics: public G4EmStandardPhysics_option4
{
    public:
    explicit SimPhysics(G4int ver = 1, const G4String &name = "");

    virtual ~SimPhysics();

    virtual void ConstructParticle();
    virtual void ConstructProcess();
};

#endif