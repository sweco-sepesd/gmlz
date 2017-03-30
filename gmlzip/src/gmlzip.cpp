//============================================================================
// Name        : gmlzip.cpp
// Author      : Peter Segestedt
// Version     :
// Copyright   : Peter Segerstedt 2017
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <iostream>
#include "gmlz.h"

std::string dir_name(std::string const & path)
{
	std::string::size_type idx;

	idx = path.find_last_of("/\\");

	if(idx != std::string::npos)
	    return path.substr(0, idx);
	return path;
}


std::string base_name(std::string const & path)
{
	std::string::size_type idx;

	idx = path.find_last_of('.');

	if(idx != std::string::npos)
	    return path.substr(0, idx);
	return path;
}

std::string file_name(std::string const & path)
{
	std::string::size_type idx;

	idx = path.find_last_of("/\\");

	if(idx != std::string::npos)
	    return path.substr(idx+1);
	return path;
}


std::string file_ext(std::string const & path)
{
	std::string::size_type idx;

	idx = path.rfind('.');

	if(idx != std::string::npos)
	    return path.substr(idx+1);
	return "";
}
int main(int argc, char * argv[]) {
	if(argc < 2) {
		fprintf (stderr, "Error\nusage: gmlzip filepath\n");
		return 1;
	}
	std::string filepath(argv[1]);
	std::string dirname(dir_name(filepath));
	std::string filename(file_name(filepath));
	std::string basename(base_name(filename));
	std::string ext(file_ext(filename));

	std::cout << gmlz::banner() << std::endl;
	std::cout << filepath.c_str() << std::endl;
	std::cout << dirname.c_str() << std::endl;
	std::cout << filename.c_str() << std::endl;
	std::cout << basename.c_str() << std::endl;
	std::cout << ext.c_str() << std::endl;

	return 0;
}
