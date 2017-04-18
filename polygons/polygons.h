#ifndef POLYGONS_H_INCLUDED
#define POLYGONS_H_INCLUDED

#ifndef POLYGONS_API
#include "polygons_export.h"
#define POLYGONS_API polygons_EXPORT
#endif

#ifdef __cplusplus
#include <vector>
#include <array>

#include "point.h"

class polygons_context
{
  public:
    polygons_context();
    ~polygons_context();

    void add_polygon(const int num_points, const double x[], const double y[]);
    void contains_points(const int num_points,
                         const double x[],
                         const double y[],
                         bool contains_points[]) const;

  private:
    polygons_context(const polygons_context &rhs);            // not implemented
    polygons_context &operator=(const polygons_context &rhs); // not implemented

    int num_polygons;
    std::vector<std::array<point, 2>> bounding_box;
    std::vector<std::vector<point>> polygons_v;

    // FIXME
    void check_that_context_is_initialized() const;
    bool is_initialized = false;
};
#endif

#ifdef __cplusplus
extern "C" {
#endif

#ifndef __cplusplus
struct polygons_context_s;
typedef struct polygons_context_s polygons_context;
#endif

POLYGONS_API
polygons_context *polygons_new_context();

POLYGONS_API
void polygons_free_context(polygons_context *context);

POLYGONS_API
void polygons_add_polygon(polygons_context *context,
                          const int num_points,
                          const double x[],
                          const double y[]);

POLYGONS_API
void polygons_contains_points(const polygons_context *context,
                              const int num_points,
                              const double x[],
                              const double y[],
                              bool contains_points[]);

#ifdef __cplusplus
}
#endif

#endif /* POLYGONS_H_INCLUDED */