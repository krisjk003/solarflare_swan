set project_name "solar_flare"
set project_dir "/home/jyothish/solar-flare-swan-fpga/vivado/solar_flare"
set part_name "xc7z010clg400-1"

create_project $project_name $project_dir -part $part_name -force

set_property target_language Verilog [current_project]

puts "========================================"
puts "Solar Flare Vivado Project Created"
puts "Project : $project_name"
puts "Part    : $part_name"
puts "========================================"

close_project
exit
