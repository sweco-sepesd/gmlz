
#include "gmlz.h"
#include <algorithm>
#include <string>
#include <sstream>
#include <stdio.h>
#include <iostream>
#include <cstdio>

namespace gmlz
{

std::string banner()
{
    char buffer[100];
    _snprintf(buffer, 100, "gmlz version %d.%d (%s)", GMLZ_MAJOR_VERSION, GMLZ_MINOR_VERSION, GMLZ_ARCH);
    return std::string(buffer);
}

DbMan::DbMan(const char *fp): _filepath(fp), _n_elements(0)
{
}

int  DbMan::_prepare()
{
    char *zErrMsg = 0;
    int rc = sqlite3_exec(_db, "create table gml_id(pos integer primary key, size integer, gml_id varchar)", DbMan::tableCreatedHandler, this, &zErrMsg);
    if (rc != SQLITE_OK)
    {
        fprintf(stderr, "SQL error: %s\n", zErrMsg);
        sqlite3_free(zErrMsg);
        //return rc;
    }
    rc = sqlite3_prepare_v2(_db, "insert into gml_id(pos, size, gml_id) values (?,?,?)",  -1, &_stmt_insert_gmlid, 0);
    if (rc != SQLITE_OK)
    {
        fprintf(stderr, "SQL error: %s\n", zErrMsg);
        sqlite3_free(zErrMsg);
        return rc;
    }
    printf("\nThe gml_id insert statement has %d wildcards\n", sqlite3_bind_parameter_count(_stmt_insert_gmlid));
    return 0;
}

void DbMan::open(bool overwrite)
{
    if(overwrite)
    {
        FilePath dbFilePath(_filepath.c_str());
        if(dbFilePath.exists())
        {
            dbFilePath.remove();
        }
    }
    int rc = sqlite3_open(_filepath.c_str(), &_db);
    if (rc)
    {
        fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(_db));
        sqlite3_close(_db);
    }
    rc = _prepare();

}

int DbMan::tableCreated(int argc, char **argv, char **azColName){
    fprintf(stdout, "callback %d\n", argc);
    return 0;
}

int DbMan::importGml(const char *fp)
{
    int BUFF_SIZE = 4096;
	if (FILE *fh = fopen(fp, "r"))
	{
        _parser = XML_ParserCreateNS(NULL, GMLZ_NS_SEP);
            
        XML_SetUserData(_parser, this);
        XML_SetElementHandler(_parser, DbMan::startElementHandler, DbMan::endElementHandler);
	    int len = 0;
		bool fSuccess = true;
        sqlite3_exec(_db, "begin transaction", NULL, NULL, NULL);
		while (!feof (fh) && fSuccess)
	    {
			void *buff = XML_GetBuffer(_parser, BUFF_SIZE);
			len = fread(buff, 1,  BUFF_SIZE, fh);
			if (XML_STATUS_ERROR == XML_ParseBuffer(_parser, len, len == 0))
			{
				std::cout << "ERROR: " << XML_ErrorString(XML_GetErrorCode(_parser)) << " (" << XML_GetErrorCode(_parser) << ")";
				std::cout << " at line " << XML_GetCurrentLineNumber(_parser) << std::endl;
				break;
			}
	    }
        if (_tracked_elements.size())
        {
            if (_tracked_elements.back().is_closed())
            {
                long end_pos = XML_GetCurrentByteIndex(_parser);
                _insert_gml_id(_tracked_elements.back(), end_pos);
                _tracked_elements.pop_back();
            }
        }
	    XML_ParserFree(_parser);
	    fclose(fh);
        
        sqlite3_exec(_db, "create unique index ix_gml_id on gml_id(gml_id)", NULL, NULL, NULL);
        sqlite3_exec(_db, "end transaction", NULL, NULL, NULL);
		std::cout << "n elements: " << _n_elements << std::endl;
 	}
	else
	{
	    return 1;
	}
    return 0;
}

int DbMan::_insert_gml_id(TrackedElement el, long end_pos) //(long position, const char *gml_id)
{
    long position = el.position();
    const char *gml_id = el.gmlId();
    sqlite3_reset(_stmt_insert_gmlid);

    if (sqlite3_bind_int64(
            _stmt_insert_gmlid,
            1, // Index of wildcard
            position) != SQLITE_OK)
    {
        printf("\nCould not bind int64.\n");
        return 1;
    }
    
    if (sqlite3_bind_int64(
            _stmt_insert_gmlid,
            2, // Index of wildcard
            end_pos - position) != SQLITE_OK)
    {
        printf("\nCould not bind int64.\n");
        return 1;
    }

    if (sqlite3_bind_text(
            _stmt_insert_gmlid,
            3, // Index of wildcard
            gml_id,
            strlen(gml_id), // length of text
            SQLITE_STATIC) != SQLITE_OK)
    {
        printf("\nCould not bind text.\n");
        return 1;
    }

    if (sqlite3_step(_stmt_insert_gmlid) != SQLITE_DONE)
    {
        printf("\nCould not step (execute) stmt.\n");
        return 1;
    }

    _n_elements++;
    return 0;
}

void DbMan::startElement(const char *el, const char **attr)
{
    // first see if back of tracked elements is closed
    if (_tracked_elements.size())
    {
        if (_tracked_elements.back().is_closed())
        {
            long end_pos = XML_GetCurrentByteIndex(_parser);
            _insert_gml_id(_tracked_elements.back(), end_pos);
            _tracked_elements.pop_back();
        }
    }

    _xml_path.push_back(gmlz::QName(el));
    for (int i = 0; attr[i]; i += 2) {
		gmlz::QName attr_qname(attr[i]);
		if(attr_qname.isGmlId())
		{
            long position = XML_GetCurrentByteIndex(_parser);
            std::string gml_id(attr[i + 1]);
            //std::cout << "begin " << position << " " << _xml_path.size() << " " << gml_id << std::endl;
            _tracked_elements.push_back(TrackedElement(_xml_path.size(), _xml_path.back(), gml_id, position));
            //_insert_gml_id(position, attr[i + 1]);
			break;
		}
    }
}

void DbMan::endElement(const char *el)
{
    gmlz::QName qname(el);
    //std::cout << "end " << el << std::endl;
    if (_tracked_elements.size())
    {
        if (_tracked_elements.back().is_closed())
        {
            long end_pos = XML_GetCurrentByteIndex(_parser);
            _insert_gml_id(_tracked_elements.back(), end_pos);
            _tracked_elements.pop_back();
        }
        if (_tracked_elements.back().matches(_xml_path.size(), qname))
        {
            _tracked_elements.back().close();
        }
    }
    _xml_path.pop_back();
}

DbMan::~DbMan()
{
    sqlite3_finalize(_stmt_insert_gmlid);
    sqlite3_close(_db);
    fprintf(stdout, "Bye from DbMan %d\n", _n_elements);
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
void FilePath::remove()
{

  if( std::remove( _filepath.c_str() ) != 0 )
    std::cout << "Error deleting file " << _filepath <<  std::endl;
  else
    std::cout << "Deleted existing file " << _filepath << std::endl;
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
bool QName::equals(QName other)
{
    return _qname == other._qname;
}

QName::~QName() {}

TrackedElement::TrackedElement(int depth, QName qname, std::string gml_id, long stream_pos) : _qname(qname),
                                                                                              _gml_id(gml_id),
                                                                                              _closed(false)
{
    _depth = depth;
    _stream_pos = stream_pos;
}
bool TrackedElement::matches(int depth, QName qname)
{
    return _depth == depth && _qname.equals(qname);
}

void TrackedElement::close()
{
    _closed = true;
}
bool TrackedElement::is_closed()
{
    return _closed;
}
const char* TrackedElement::gmlId(){
    return _gml_id.c_str();
}
long TrackedElement::position(){
    return _stream_pos;
}
TrackedElement::~TrackedElement() {}

} // namespace gmlz