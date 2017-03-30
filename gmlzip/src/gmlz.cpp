
#include "gmlz.h"
#include <algorithm>
#include <string>
#include <sstream>
#include <stdio.h>

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
    rc = sqlite3_exec(_db, "CREATE TABLE msg(a int)", c_callback, this, &zErrMsg);
    if (rc != SQLITE_OK)
    {
        fprintf(stderr, "SQL error: %s\n", zErrMsg);
        sqlite3_free(zErrMsg);
    }
}
int DbMan::callback(int argc, char **argv, char **azColName){
    fprintf(stdout, "callback %d\n", argc);
    return 0;
}
DbMan::~DbMan()
{
    sqlite3_close(_db);
    fprintf(stdout, "Bye from DbMan\n");
}



static int c_callback(void *param, int argc, char **argv, char **azColName)
{
    DbMan* dbMan = reinterpret_cast<DbMan*>(param);
    return dbMan->callback(argc, argv, azColName);
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
std::string FilePath::dirname()
{
    std::ostringstream ss;
    std::for_each(_dir_parts.begin(), _dir_parts.end(), [&ss](const std::string &s) { ss << s; });
    ss << GMLZ_FILESEP;
    return ss.str();
}
FilePath::~FilePath() {}
} // namespace gmlz