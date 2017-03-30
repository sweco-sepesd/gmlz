//============================================================================
// Name        : gmlzip.cpp
// Author      : Peter Segestedt
// Version     :
// Copyright   : Peter Segerstedt 2017
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <iostream>
#include <sstream>
#include "gmlz.h"

int main(int argc, char *argv[])
{
    if (argc < 2)
    {
	fprintf(stderr, "Error\nusage: gmlzip filepath\n");
	return 1;
    }
    gmlz::FilePath source_file(argv[1]);

    if (source_file.exists())
    {
	std::cout << gmlz::banner() << std::endl;
	std::cout << source_file.dirname() << source_file.basename() << source_file.ext() << std::endl;
	std::ostringstream ss;
	ss << source_file.dirname() << source_file.basename() << ".db";
	std::string dbPath(ss.str());
	std::cout << dbPath << std::endl;

	gmlz::DbMan db(dbPath.c_str());
	db.open();
	
	return 0;
    }

    return 1;
}
