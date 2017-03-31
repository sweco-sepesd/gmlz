
#include "gmlz.h"
#include <algorithm>
#include <string>
#include <sstream>
#include <stdio.h>
#include <iostream>

namespace gmlz
{

std::string banner()
{
    char buffer[100];
    _snprintf(buffer, 100, "gmlz version %d.%d (%s)", GMLZ_MAJOR_VERSION, GMLZ_MINOR_VERSION, GMLZ_ARCH);
    return std::string(buffer);
}

DbMan::DbMan(const char *fp): _filepath(fp)
{
}

void DbMan::open()
{
    int rc = sqlite3_open(_filepath.c_str(), &_db);
    if (rc)
    {
        fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(_db));
        sqlite3_close(_db);
    }
    char *zErrMsg = 0;
    rc = sqlite3_exec(_db, "CREATE TABLE gmlid(offset integer primary key, id varchar)", DbMan::tableCreatedHandler, this, &zErrMsg);
    if (rc != SQLITE_OK)
    {
        fprintf(stderr, "SQL error: %s\n", zErrMsg);
        sqlite3_free(zErrMsg);
    }
}
int DbMan::tableCreated(int argc, char **argv, char **azColName){
    fprintf(stdout, "callback %d\n", argc);
    return 0;
}

void DbMan::importGml(const char *fp)
{
//TODO: Move parsing from gmlzip main to here
}

void DbMan::startElement(const char *el, const char **attr)
{
    for (int i = 0; attr[i]; i += 2) {
		gmlz::QName qname(attr[i]);
		if(qname.isGmlId())
		{
			//n_elements++;
			std::string val(attr[i + 1]);
			//std::cout << val << std::endl;
		}
    }
}

DbMan::~DbMan()
{
    sqlite3_close(_db);
    fprintf(stdout, "Bye from DbMan\n");
}

FilePath::FilePath(const char *src) : _filepath(src)
{
    std::string::size_type pos;
    std::string::size_type last_pos;
    last_pos = 0;
    pos = _filepath.find_first_of("/\\");
    while (pos != std::string::npos)
    {
        _dir_parts.push_back(_filepath.substr(last_pos, pos - last_pos));
        last_pos = pos;
        pos = _filepath.find_first_of("/\\", pos + 1);
    }
    if (last_pos > 0 && last_pos + 1 != std::string::npos)
    {
        std::string filename = _filepath.substr(last_pos + 1);

        pos = filename.find_last_of('.');

        if (pos != std::string::npos)
        {
            _filename_parts.push_back(filename.substr(0, pos));
            _filename_parts.push_back(filename.substr(pos));
        }
    }
}

std::string FilePath::ext()
{
    return _filename_parts[1];
}
std::string FilePath::basename()
{
    return _filename_parts[0];
}
bool FilePath::exists()
{
    if (FILE *file = fopen(_filepath.c_str(), "r"))
    {
        fclose(file);
        return true;
    }
    else
    {
        return false;
    }
}

std::string FilePath::filename()
{
    std::ostringstream ss;
    std::for_each(_filename_parts.begin(), _filename_parts.end(), [&ss](const std::string &s) { ss << s; });
    return ss.str();
}
std::string FilePath::filepath()
{
    return std::string(_filepath);
}
std::string FilePath::dirname()
{
    std::ostringstream ss;
    std::for_each(_dir_parts.begin(), _dir_parts.end(), [&ss](const std::string &s) { ss << s; });
    ss << GMLZ_FILESEP;
    return ss.str();
}
FilePath::~FilePath() {}

QName::QName(const char *qname) : _qname(qname)
{
    std::string::size_type pos;
    pos = _qname.find(GMLZ_NS_SEP);
    if (pos != std::string::npos) 
    {
        _ns = _qname.substr(0, pos);
        _localname = _qname.substr(pos + 1);
    }
}

bool QName::isGmlId()
{
    if((_ns == GMLZ_GML_NS || _ns == GMLZ_GML_32_NS) && _localname == "id")
        return  true;
    return false;
}

QName::~QName() {}

} // namespace gmlz