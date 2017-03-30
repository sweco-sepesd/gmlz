#ifndef GMLZ_H
#define GMLZ_H

#define GMLZ_MAJOR_VERSION 0
#define GMLZ_MINOR_VERSION 1

#include <string>
#include <vector>
#include "sqlite3.h"

#ifdef _WIN32
#define GMLZ_FILESEP "\\"
#ifdef _WIN64
#define GMLZ_ARCH "win64"
#else
#define GMLZ_ARCH "win32"
#endif
#elif __APPLE__
#define GMLZ_FILESEP "/"
#include "TargetConditionals.h"
#if TARGET_IPHONE_SIMULATOR
#define GMLZ_ARCH "ios_sim"
#elif TARGET_OS_IPHONE
#define GMLZ_ARCH "ios"
#elif TARGET_OS_MAC
#define GMLZ_ARCH "unknown osx"
#else
#define GMLZ_ARCH "unknown apple"
#endif
#elif __linux__
#define GMLZ_FILESEP "/"
#define GMLZ_ARCH "linux"
#elif __unix__ // all unices not caught above
#define GMLZ_FILESEP "/"
#define GMLZ_ARCH "unix"
#elif defined(_POSIX_VERSION)
#define GMLZ_FILESEP "/"
#define GMLZ_ARCH "posix"
#else
#define GMLZ_FILESEP "/"
#define GMLZ_ARCH "unknown"
#endif

namespace gmlz
{

static int c_callback(void *param, int argc, char **argv, char **azColName);

std::string banner();

class DbMan
{
    sqlite3 *_db;
    std::string _filepath;

  public:
    DbMan(const char *fp);
    void open();
    int callback(int argc, char **argv, char **azColName);
    virtual ~DbMan();
};

class FilePath
{
    std::string _filepath;
    std::vector<std::string> _dir_parts;
    std::vector<std::string> _filename_parts;

  public:
    FilePath(const char *src);
    std::string basename();
    std::string dirname();
    std::string ext();
    std::string filename();
    bool exists();

    virtual ~FilePath();
};

} // namespace gmlz

#endif