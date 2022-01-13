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
/// \file FilePrinter.hh
/// \brief Definition of the FilePrinter class

#ifndef FILE_PRINTER_h
#define FILE_PRINTER_h 1

// #include <fstream>
#include <iostream>
#include <sstream>

class FilePrinter
{
protected:
    static std::stringstream ss;

public:
    FilePrinter() = default;
    static std::stringstream &GetStreamForWrite() {return ss;}
    static void ClearStream() {ss.str("");}
    static std::string GetStringForFile() { return ss.str(); }
    static std::string GetStringAndReset()
    {
        std::string temp = GetStringForFile();
        ClearStream();
        return std::move(temp);
    };
    ~FilePrinter();
};

#endif