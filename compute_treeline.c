#include <stdio.h>
#include <stdlib.h>
#include <vicNl.h>

static char vcid[] = "$Id$";

void compute_treeline(atmos_data_struct        *atmos,
                      dmy_struct               *dmy,
		      double                   *Tfactor,
		      char                     *AboveTreeLine)
/**********************************************************************
  compute_treeline.c        Keith Cherkauer          March 12, 2003

  This routine computes the annual average July temperature for the 
  current gridcell.  The temperature is than lapsed to determine the 
  elevation at which the annual average temperature is equal to 10C.
  Snow elevation bands above this elevation are considered to be above
  the treeline.  When gridcell data is output at the end of each time 
  step, vegetation types with overstory will be excluded from the 
  variable averages of snow bands higher than the treeline (e.g. decidous
  trees will be removed from high elevation snow bands, while grass
  and shrubs will remain).  This is to serve as a preliminary fix for
  high elevation "glaciers", a more permanent version would actually 
  allow for vegetation types to be excluded from various snow bands.

************************************************************************/
{

  extern option_struct       options;
  extern global_param_struct global_param;
  extern int                 NR, NF;

  double MonthSum;
  double AnnualSum;
  int    MonthCnt;
  int    AnnualCnt;
  int    rec;
  int    band;
  int    i;

  AnnualSum = 0;
  AnnualCnt = 0;
  rec = 0;
  while ( rec < global_param.nrecs ) {
    if ( dmy[rec].month == 7 ) {
      MonthSum = 0;
      MonthCnt = 0;
      while ( dmy[rec].month == 7 ) {
	for (i = 0; i < NF; i++) {
	  MonthSum += atmos[rec].air_temp[i];
	  MonthCnt++;
	}
	rec++;
      }
      if ( MonthCnt > 0 ) {
	// Sum monthly average July temperature
	AnnualSum += MonthSum / (double)MonthCnt;
	AnnualCnt++;
      }
    }
    rec++;
  }

  // Compute average annual July sir temperature
  if ( AnnualCnt > 0 )
    AnnualSum /= (double)AnnualCnt;

  // Lapse average annual July air temperature to 10C and determine elevation
  for ( band = 0; band < options.SNOW_BAND; band++ ) {
    if ( AnnualSum + Tfactor[band] <= 10. ) 
      // Band is above treeline
      AboveTreeLine[band] = TRUE;
    else
      AboveTreeLine[band] = FALSE;
  }
}
