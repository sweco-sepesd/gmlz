#ifndef GMLZ_H
#define GMLZ_H

#define GMLZ_MAJOR_VERSION 0
#define GMLZ_MINOR_VERSION 1

#include <string>

#ifdef _WIN32
   #ifdef _WIN64
      #define GMLZ_ARCH "win64"
   #else
   	   #define GMLZ_ARCH "win32"
   #endif
#elif __APPLE__
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
    #define GMLZ_ARCH "linux"
#elif __unix__ // all unices not caught above
    #define GMLZ_ARCH "unix"
#elif defined(_POSIX_VERSION)
    #define GMLZ_ARCH "posix"
#else
    #define GMLZ_ARCH "unknown"
#endif

namespace gmlz {

std::string banner();


} // namespace gmlz

#endif