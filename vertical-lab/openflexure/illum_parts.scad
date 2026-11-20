// wrapper: one part of reflection_illuminator_LED_star.scad in its design frame
use <./reflection_illuminator_LED_star.scad>;
PART = "holder";
if (PART == "holder") illuminator_holder();
if (PART == "lens_holder") lens_holder();
