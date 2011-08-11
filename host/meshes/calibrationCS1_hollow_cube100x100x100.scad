



translate ([ 0,0,0]) difference(){
	cube( [ 100, 100, 100 ], center=true );
	translate( [ 0, 0, -1] ) cube( [ 50, 50, 104 ], center=true );
	translate( [-1, 0, 0] ) cube( [ 104, 50, 50 ], center=true );
	translate( [ 0,-1, 0] ) cube( [ 50, 104, 50 ], center=true );

}