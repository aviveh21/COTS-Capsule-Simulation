#include "SimPhysics.hh"
#include "G4PhysicsConstructorFactory.hh"
#include "G4SystemOfUnits.hh"

#include "G4MicroElecElastic.hh"
#include "G4MicroElecElasticModel.hh"

#include "G4MicroElecInelastic.hh"
#include "G4MicroElecInelasticModel.hh"

#include "G4LossTableManager.hh"
#include "G4EmConfigurator.hh"
#include "G4VEmModel.hh"
#include "G4DummyModel.hh"
#include "G4eIonisation.hh"
#include "G4hIonisation.hh"
#include "G4ionIonisation.hh"
#include "G4eMultipleScattering.hh"
#include "G4hMultipleScattering.hh"
#include "G4BraggModel.hh"
#include "G4BraggIonModel.hh"
#include "G4BetheBlochModel.hh"
#include "G4UrbanMscModel.hh"
#include "G4MollerBhabhaModel.hh"
#include "G4IonFluctuations.hh"
#include "G4UniversalFluctuation.hh"

#include "G4ElectronCapture.hh"

#include "G4UAtomicDeexcitation.hh"

#include "G4VUserPhysicsList.hh"
#include "G4ProcessManager.hh"
#include "G4ParticleTypes.hh"

G4_DECLARE_PHYSCONSTR_FACTORY(SimPhysics);

SimPhysics::SimPhysics(G4int ver, const G4String &name) : G4EmStandardPhysics_option4(ver, name)
{}

void SimPhysics::ConstructProcess()
{
    G4EmStandardPhysics_option4::ConstructProcess();
auto particleIterator=GetParticleIterator();
  particleIterator->reset();
  
  while( (*particleIterator)() )
  {

    G4ParticleDefinition* particle = particleIterator->value();
    G4ProcessManager* pmanager = particle->GetProcessManager();
    G4String particleName = particle->GetParticleName();

    // *********************************
    // 1) Processes for the World region
    // *********************************

    if (particleName == "e-") {

      // STANDARD msc is active in the world

      // STANDARD ionisation is active in the world

      // MicroElec elastic is not active in the world 
      G4MicroElecElastic* theMicroElecElasticProcess = new G4MicroElecElastic("e-_G4MicroElecElastic");
      theMicroElecElasticProcess->SetEmModel(new G4DummyModel(),1);
      pmanager->AddDiscreteProcess(theMicroElecElasticProcess);

      // MicroElec ionisation is not active in the world 
      G4MicroElecInelastic* microelecioni = new G4MicroElecInelastic("e-_G4MicroElecInelastic");
      microelecioni->SetEmModel(new G4DummyModel(),1); 
      pmanager->AddDiscreteProcess(microelecioni);

      // THE FOLLOWING PROCESS WILL KILL ALL ELECTRONS BELOW A SELECTED ENERY THRESHOLD
      // Capture of low-energy e-
      G4ElectronCapture* ecap = new G4ElectronCapture("Target", 16.7*eV);
      pmanager->AddDiscreteProcess(ecap);
     	    
    } else if ( particleName == "proton" ) {

      // STANDARD msc is active in the world 

      // STANDARD ionisation is active in the world 
      G4hIonisation* hion = new G4hIonisation();
      pmanager->AddProcess(hion, -1, 2, 2);

      // MicroElec ionisation is not active in the world 
      G4MicroElecInelastic* microelecioni = new G4MicroElecInelastic("p_G4MicroElecInelastic");
      microelecioni->SetEmModel(new G4DummyModel(),1); 
      microelecioni->SetEmModel(new G4DummyModel(),2); 
      pmanager->AddDiscreteProcess(microelecioni);

    } else if (particleName == "GenericIon") { 

      // STANDARD msc is active in the world 
      G4hMultipleScattering* msc = new G4hMultipleScattering();
      msc->AddEmModel(1, new G4UrbanMscModel());
      pmanager->AddProcess(new G4hMultipleScattering, -1, 1, -1);

      // STANDARD ionisation is active in the world 

      // MicroElec ionisation is not active in the world 
      G4MicroElecInelastic* microelecioni = new G4MicroElecInelastic("ion_G4MicroElecInelastic");
      microelecioni->SetEmModel(new G4DummyModel(),1); 
      microelecioni->SetEmModel(new G4DummyModel(),2);
      pmanager->AddDiscreteProcess(microelecioni);
    } 
  }

  // ------- Target: --------

    G4EmConfigurator* em_config = G4LossTableManager::Instance()->EmConfigurator();

  G4VEmModel* mod;
  // *** e-

  // ---> STANDARD EM processes are inactivated below 100 MeV
  
  G4UrbanMscModel* msc =  new G4UrbanMscModel();
  msc->SetActivationLowEnergyLimit(100*MeV);
  em_config->SetExtraEmModel("e-","msc",msc,"Target");
  
  mod = new G4MollerBhabhaModel();
  mod->SetActivationLowEnergyLimit(100*MeV);
  em_config->SetExtraEmModel("e-","eIoni",mod,"Target",0.0,10*TeV, new G4UniversalFluctuation());

  // ---> MicroElec processes activated

  mod = new G4MicroElecElasticModel();
  em_config->SetExtraEmModel("e-","e-_G4MicroElecElastic",mod,"Target",0.0,100*MeV);
  
  mod = new G4MicroElecInelasticModel();
  em_config->SetExtraEmModel("e-","e-_G4MicroElecInelastic",mod,"Target",16.7*eV,100*MeV);

  // *** proton
  
  // ---> STANDARD EM processes inactivated below standEnergyLimit

  // STANDARD msc is still active
  // Inactivate following STANDARD processes 
    
  mod = new G4BraggModel();
  mod->SetActivationHighEnergyLimit(50*keV);
  em_config->SetExtraEmModel("proton","hIoni",mod,"Target",0.0,2*MeV, new G4IonFluctuations());
    
  mod = new G4BetheBlochModel();
  mod->SetActivationLowEnergyLimit(10*GeV);
  em_config->SetExtraEmModel("proton","hIoni",mod,"Target",2*MeV,10*TeV, new G4IonFluctuations());
			     
  // ---> MicroElec processes activated  
  mod = new G4MicroElecInelasticModel(); 
  mod->SetActivationLowEnergyLimit(50*keV);
  em_config->SetExtraEmModel("proton","p_G4MicroElecInelastic",mod,"Target",0.0,10*GeV);
  em_config->SetExtraEmModel("proton","p_G4MicroElecInelastic",new G4DummyModel,
			     "Target",10*GeV,10*TeV);

 // *** ion

  // ---> STANDARD EM processes inactivated below standEnergyLimit

  // STANDARD msc is still active
  // Inactivate following STANDARD processes 

  mod = new G4BraggIonModel();
  mod->SetActivationHighEnergyLimit(50*keV);
  em_config->SetExtraEmModel("GenericIon","ionIoni",mod,"Target",0.0,2*MeV, new G4IonFluctuations());
 
  mod = new G4BetheBlochModel();
  mod->SetActivationLowEnergyLimit(10*GeV);
  em_config->SetExtraEmModel("GenericIon","ionIoni",mod,"Target",2*MeV,10*TeV, new G4IonFluctuations());
   
  // ---> MicroElec processes activated
  mod = new G4MicroElecInelasticModel(); 
  mod->SetActivationLowEnergyLimit(50*keV);
  em_config->SetExtraEmModel("GenericIon","ion_G4MicroElecInelastic",mod,
			     "Target",0.0,10*GeV);
  em_config->SetExtraEmModel("GenericIon","ion_G4MicroElecInelastic",new G4DummyModel,
			     "Target",10*GeV,10*TeV);

  // Deexcitation
  //
  G4VAtomDeexcitation* de = new G4UAtomicDeexcitation();
  G4LossTableManager::Instance()->SetAtomDeexcitation(de);
  de->SetFluo(true);
  de->SetAuger(true);   
  de->SetPIXE(true);  
  de->InitialiseForNewRun();
}

void SimPhysics::ConstructParticle()
{
    G4EmStandardPhysics_option4::ConstructParticle();
}

SimPhysics::~SimPhysics()
{}