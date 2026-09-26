/* Lets Bambu Studio's statically linked, GLX-only GLEW initialise on the
 * OSMesa context that its Linux CLI asks GLFW for (headless thumbnails).
 * Preload together with libOSMesa.so.8 so plain gl* calls resolve to OSMesa. */
#include <string.h>
typedef void (*fp)(void);
extern fp OSMesaGetProcAddress(const char *name);
static char fake_display[4096];
static void *get_current_display(void) { return fake_display; }
fp glXGetProcAddressARB(const unsigned char *name)
{
    if (!strcmp((const char *)name, "glXGetCurrentDisplay"))
        return (fp)get_current_display;
    return OSMesaGetProcAddress((const char *)name);
}
fp glXGetProcAddress(const unsigned char *name) { return glXGetProcAddressARB(name); }
int glXQueryVersion(void *dpy, int *major, int *minor)
{
    (void)dpy;
    if (major) *major = 1;
    if (minor) *minor = 4;
    return 1;
}
const char *glXGetClientString(void *dpy, int name) { (void)dpy; (void)name; return ""; }
