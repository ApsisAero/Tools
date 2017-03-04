res = 100;

function toMM(n) = 25.4 * n;

or = toMM(0.375);
ir = toMM(0.1875);

side_thick = toMM(0.09375);
bottom_thick = toMM(0.1875);
wall_height = toMM(2/3);

curve_rad = toMM(0.125);

module casting_end() {
    linear_extrude(height=bottom_thick) difference() {
        minkowski() {
            square([2*(or+side_thick),4*(or+side_thick)],center=true);
            circle(curve_rad, $fn=res);
        }
        circle(ir, $fn=res);
    }
    translate([0,0,bottom_thick]) linear_extrude(height=wall_height) {
        difference() {
            circle(or+side_thick, $fn=res);
            circle(or, $fn=res);
        }
    }
    translate([0,0,bottom_thick]) mirror([0,0,1]) rotate_extrude(angle=360, $fn=res) {
        translate([or+side_thick+curve_rad,-curve_rad]) mirror([1,0]) difference() {
            square([curve_rad,curve_rad]);
            circle(curve_rad, $fn=res);
        }
    }
}

casting_rod_height = toMM(1);
casting_rod_base = toMM(0.625);
casting_rod_curve_rad = toMM(0.09375);

module casting_rod() {
    linear_extrude(height=bottom_thick) minkowski() {
        square([casting_rod_base,casting_rod_base], center=true);
        circle(casting_rod_curve_rad, $fn=res);
    }
    translate([0,0,bottom_thick]) mirror([0,0,1]) rotate_extrude(angle=360, $fn=res) {
        translate([ir+casting_rod_curve_rad,-casting_rod_curve_rad]) mirror([1,0]) difference() {
            square([casting_rod_curve_rad,casting_rod_curve_rad]);
            circle(casting_rod_curve_rad, $fn=res);
        }
    }
    translate([0,0,bottom_thick]) cylinder(casting_rod_height, ir, ir, $fn=res);
}

module end_group(num_end_x, num_end_y) {
    dx = 2*(or+side_thick)+2*curve_rad+2;
    dy = 4*(or+side_thick)+2*curve_rad+2;
    total_x = (num_end_x-1)*dx;
    total_y = (num_end_y-1)*dy;
    for(i=[0:num_end_x-1]) translate([i*dx+ir+link_x/2,total_y/2,link_z/2]) cube([link_x,total_y,link_z],center=true);
    for(i=[0:num_end_y-1]) translate([total_x/2,i*dy+ir+link_y/2,link_z/2]) cube([total_x,link_y,link_z],center=true);
    for(i=[0:num_end_x-1]) for(j=[0:num_end_y-1]) translate([i*dx,j*dy]) casting_end();
}
module rod_group(num_rod_x, num_rod_y) {
    dx = 2*(casting_rod_base/2+casting_rod_curve_rad)+2;
    dy = 2*(casting_rod_base/2+casting_rod_curve_rad)+2;
    total_x = (num_rod_x-1)*dx;
    total_y = (num_rod_y-1)*dy;
    for(i=[0:num_rod_x-1]) translate([i*dx+link_x/2,total_y/2,link_z/2]) cube([link_x,total_y,link_z],center=true);
    for(i=[0:num_rod_y-1]) translate([total_x/2,i*dy+link_y/2,link_z/2]) cube([total_x,link_y,link_z],center=true);
    for(i=[0:num_rod_x-1]) for(j=[0:num_rod_y-1]) translate([i*dx,j*dy]) casting_rod();
}

link_x = 1;
link_y = 1;
link_z = 1;

rndr = "rod";
if(rndr == "end") {
    end_group(3,2);
    translate([0,2*(or+side_thick)+curve_rad+1,2*bottom_thick+wall_height+1]) mirror([0,0,1]) end_group(3,2);
}
else if(rndr == "rod") {
    rod_group(2,4);
    translate([0,casting_rod_base/2+casting_rod_curve_rad+1,2*bottom_thick+casting_rod_height+1]) mirror([0,0,1]) rod_group(2,4);
}