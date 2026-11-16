#include <gutenprint/gutenprint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
static FILE *out; static int W=720, H=360, CH=6;
static void wr(void*d,const char *b,size_t n){fwrite(b,1,n,out);}
static void er(void*d,const char *b,size_t n){fwrite(b,1,n,stderr);}
static int iw(stp_image_t*i){return W;} static int ih(stp_image_t*i){return H;}
static stp_image_status_t gr(stp_image_t*i,unsigned char*data,size_t bl,int row){
  unsigned short*d=(unsigned short*)data; if(row==0)fprintf(stderr,"bl=%zu need=%d\n",bl,W*CH*2); if(bl<(size_t)W*CH*2){memset(data,0,bl);return STP_IMAGE_STATUS_OK;}
  for(int x=0;x<W;x++)for(int c=0;c<CH;c++){ d[x*CH+c]= getenv("ROWBAND") ? ((row>=100&&row<110)?65535:0) : ((x/(W/CH)==c)? 65535:0); }
  return STP_IMAGE_STATUS_OK;}
static void noop(stp_image_t*i){}
static const char* nm(stp_image_t*i){return "ref";}
int main(int argc,char**argv){
  stp_init(); out=fopen(argv[1],"wb");
  stp_vars_t *v=stp_vars_create();
  const stp_printer_t*p=stp_get_printer_by_driver(argv[2]);
  if(!p){fprintf(stderr,"no printer\n");return 1;}
  stp_set_printer_defaults(v,p);
  stp_set_driver(v,argv[2]);
  stp_set_outfunc(v,wr); stp_set_errfunc(v,er);
  stp_set_string_parameter(v,"InputImageType","Raw");
  stp_set_string_parameter(v,"RawChannels","6"); stp_set_string_parameter(v,"ChannelBitDepth","16");
  stp_set_string_parameter(v,"PrintingMode","Color");
  stp_set_string_parameter(v,"Resolution",argv[3]);
  stp_set_string_parameter(v,"PageSize","A4");
  stp_set_string_parameter(v,"InputSlot",argc>4?argv[4]:"Rear");
  double l,r,b,t; stp_get_imageable_area(v,&l,&r,&b,&t);
  fprintf(stderr,"imageable %f %f %f %f\n",l,r,b,t);
  stp_set_left(v,l+(getenv("LX")?atof(getenv("LX")):0)); stp_set_top(v,t+(getenv("TY")?atof(getenv("TY")):0)); if(getenv("ROLL"))stp_set_string_parameter(v,"MediaType","Plain"); stp_set_width(v,W*72/720); stp_set_height(v,H*72/720);
  stp_image_t im={0,0,iw,ih,gr,nm,noop,0};
  stp_start_job(v,&im); int ok=stp_print(v,&im); stp_end_job(v,&im);
  fprintf(stderr,"ok=%d\n",ok); fclose(out); return 0;}
