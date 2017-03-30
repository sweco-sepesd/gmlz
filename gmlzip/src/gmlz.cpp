
#include "gmlz.h"
#include <string>
#include <stdio.h>

namespace gmlz {

    std::string banner() {
        char buffer [100];
        _snprintf ( buffer, 100, "gmlz version %d.%d (%s)", GMLZ_MAJOR_VERSION, GMLZ_MINOR_VERSION, GMLZ_ARCH);
        return std::string(buffer);
    }
} // namespace gmlz