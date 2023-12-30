#----------------------------------------------------------------------------
# Setup the project (THIS IS THE STATIC VERSION, Use the other CMAKE for dynamic)
cmake_minimum_required(VERSION 3.1 FATAL_ERROR)
project(Sim)

#----------------------------------------------------------------------------
# Find Geant4 package, activating all available UI and Vis drivers by default
# You can set WITH_GEANT4_UIVIS to OFF via the command line or ccmake/cmake-gui
# to build a batch mode only executable
#
find_package(Geant4 REQUIRED static)
option(WITH_GEANT4_UIVIS "Build example with Geant4 UI and Vis drivers" ON)
if(WITH_GEANT4_UIVIS)
  find_package(Geant4 REQUIRED static ui_all vis_all)
else()
  find_package(Geant4 REQUIRED static)
endif()

#----------------------------------------------------------------------------
# Setup Geant4 include directories and compile definitions
#
set(CMAKE_FIND_LIBRARY_SUFFIXES ".a")
set(BUILD_SHARED_LIBS OFF)
set(CMAKE_EXE_LINKER_FLAGS "-static")


include(${Geant4_USE_FILE})

#----------------------------------------------------------------------------
# Locate sources and headers for this project
#

include_directories(${PROJECT_SOURCE_DIR}/include 
                    ${Geant4_INCLUDE_DIR})
file(GLOB sources ${PROJECT_SOURCE_DIR}/src/*.cc)
file(GLOB headers ${PROJECT_SOURCE_DIR}/include/*.hh)

#----------------------------------------------------------------------------
# Add the executable, and link it to the Geant4 libraries
#

add_executable(Sim Sim.cc ${sources} ${headers})
target_link_libraries(Sim -static ${Geant4_LIBRARIES} )
#target_link_libraries(Sim -static )

#----------------------------------------------------------------------------
# Copy all scripts to the build directory, i.e. the directory in which we
# build Sim. This is so that we can run the executable directly because it
# relies on these scripts being in the current working directory.
#
set(Sim_SCRIPTS
    Sim.out
    Sim.in
    cerenkov.mac
    wls.mac
    photon.mac
    reviewEvent.mac
    gui.mac
    vis.mac
   )

foreach(_script ${Sim_SCRIPTS})
  configure_file(
    ${PROJECT_SOURCE_DIR}/${_script}
    ${PROJECT_BINARY_DIR}/${_script}
    COPYONLY
    )
endforeach()

#----------------------------------------------------------------------------
# Install the executable to 'bin' directory under CMAKE_INSTALL_PREFIX
#
install(TARGETS Sim DESTINATION bin)

