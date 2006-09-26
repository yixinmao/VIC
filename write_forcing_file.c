#include <stdio.h>
#include <stdlib.h>
#include <vicNl.h>

static char vcid[] = "$Id$";

#if OUTPUT_FORCE
void write_forcing_file(atmos_data_struct *atmos,
			int                nrecs,
			out_data_file_struct *out_data_files, 
			out_data_struct   *out_data)
/**********************************************************************
  write_forcing_file          Keith Cherkauer           July 19, 2000

  This routine writes the complete forcing data files for use in 
  future simulations.
  2006-08-23 Changed order of fread/fwrite statements from ...1, sizeof...
             to ...sizeof, 1,... GCT
  2006-Sep-11 Implemented flexible output configuration; uses the new
              out_data and out_data_files structures. TJB

**********************************************************************/
{
  extern option_struct options;

  int                 rec, j, v;
  short int          *tmp_siptr;
  unsigned short int *tmp_usiptr;
  dmy_struct         *dummy_dmy;
  int                 dummy_dt;

  for ( rec = 0; rec < nrecs; rec++ ) {
    for ( j = 0; j < NF; j++ ) {
      out_data[OUT_PREC].data[0] = atmos[rec].prec[j];
      out_data[OUT_AIR_TEMP].data[0] = atmos[rec].air_temp[j];
      out_data[OUT_SHORTWAVE].data[0] = atmos[rec].shortwave[j];
      out_data[OUT_LONGWAVE].data[0] = atmos[rec].longwave[j];
      out_data[OUT_DENSITY].data[0] = atmos[rec].density[j];
      out_data[OUT_PRESSURE].data[0] = atmos[rec].pressure[j];
      out_data[OUT_VP].data[0] = atmos[rec].vp[j];
      out_data[OUT_WIND].data[0] = atmos[rec].wind[j];
      if (options.BINARY_OUTPUT) {
        for (v=0; v<N_OUTVAR_TYPES; v++) {
          out_data[v].data[0] *= out_data[v].mult;
        }
      }
      write_data(out_data_files, out_data, dummy_dmy, dummy_dt);
    }
  }

}
#endif /* OUTPUT_FORCE */
