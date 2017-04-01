#ifndef GMLZ_H
#define GMLZ_H

#define GMLZ_MAJOR_VERSION 0
#define GMLZ_MINOR_VERSION 1
#define GMLZ_NS_SEP ' '

#define GMLZ_GML_NS "http://www.opengis.net/gml"
#define GMLZ_GML_32_NS "http://www.opengis.net/gml/3.2"

#include <string>
#include <vector>
#include "sqlite3.h"
#include "expat/expat.h"

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
  private:
    sqlite3 *_db;
    sqlite3_stmt *_stmt_insert_gmlid;
    std::string _filepath;
    XML_Parser _parser;
    int _n_elements;
    int _prepare();
    int _insert_gml_id(long position,  const char *gml_id);

  public:
    DbMan(const char *fp);
    void open(bool overwrite);
    int tableCreated(int argc, char **argv, char **azColName);
    int importGml(const char *fp);
    void startElement( const char *el, const char **attr);
    static void startElementHandler(void *data, const char *el, const char **attr)
    {
        static_cast<DbMan*>(data)->startElement(el, attr);
    }
    static int tableCreatedHandler(void *param, int argc, char **argv, char **azColName)
    {
        return static_cast<DbMan*>(param)->tableCreated(argc, argv, azColName);
    }
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
  std::string filepath();
  void remove();
  bool exists();

  virtual ~FilePath();
};

class QName
{
  std::string _ns;
  std::string _localname;
  std::string _qname;

public:
  QName(const char *qname);
  bool isGmlId();
  virtual ~QName();
};



} // namespace gmlz

#endif