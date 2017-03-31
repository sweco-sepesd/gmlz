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
#include "expat/expat.h"

//#define BUFF_SIZE 4096


int n_elements;

void start(void *data, const char *el, const char **attr)
{
	
	for (int i = 0; attr[i]; i += 2) {
		gmlz::QName qname(attr[i]);
		if(qname.isGmlId())
		{
			n_elements++;
			std::string val(attr[i + 1]);
			//std::cout << val << std::endl;
		}
    }
}


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
	std::string db_filepath(source_file.dirname() + source_file.basename() + ".db");
	std::cout << db_filepath << std::endl;

	gmlz::DbMan db_man(db_filepath.c_str());
	db_man.open();
	n_elements = 0;
	int BUFF_SIZE = 4096;
	if (FILE *fh = fopen(source_file.filepath().c_str(), "r"))
	{
	    XML_Parser parser = XML_ParserCreateNS(NULL, GMLZ_NS_SEP);
		
		XML_SetUserData(parser, &db_man);
		XML_SetStartElementHandler(parser, gmlz::DbMan::startElementHandler);
	    int len = 0;
		bool fSuccess = true;
		while (!feof (fh) && fSuccess)
	    {
			void *buff = XML_GetBuffer(parser, BUFF_SIZE);
			len = fread(buff, 1,  BUFF_SIZE, fh);
			if (XML_STATUS_ERROR == XML_ParseBuffer(parser, len, len == 0))
			{
				std::cout << "ERROR: " << XML_ErrorString(XML_GetErrorCode(parser)) << " (" << XML_GetErrorCode(parser) << ")";
				std::cout << " at line " << XML_GetCurrentLineNumber(parser) << std::endl;
				break;
			}
	    }

	    XML_ParserFree(parser);
	    fclose(fh);
		std::cout << "n elements: " << n_elements << std::endl;
 	}
	else
	{
	    return 1;
	}

	return 0;
    }

    return 1;
}
