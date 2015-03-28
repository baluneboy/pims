# wx demo main pane to warehouse these one-liners

# recursive wget
cd # to desired destination dir
wget -r --no-parent --reject "index.html*" http://mysite.com/configs/the_folder/

# unique sensor subdir list (almost, we want optional regex with good default to weed out undesirables)
find /misc/yoda/pub/pad -maxdepth 4 -mindepth 4 -type d -printf "%f\n" | sort | uniq

# JAXA intrms snaps go to
/jawa/pims/www/pub/plots/sams/121f05/interval_rms.jpg

# Use sed to replace string in files
sed -i 's/oldWord/newWord/g' *.txt

# Find PAD profile JPGs
find /misc/yoda/pub/pad -maxdepth 2 -name "*_padprofile.jpg"

# Find real-time screenshots done within last MAGO minutes; note the minus sign in front of ${MAGO}
MAGO=30; find /misc/yoda/www/plots/sams -mmin -${MAGO} -name "*.jpg"

# Find es05 data for a given year
find /misc/yoda/pub/pad/year2012 -maxdepth 3 -type d -name "*es05"

# AS ROOT ON JAWA, SEE ABOUT LAIBLE LINKS -- search gmail using following in search box:
label:pimsops-laible  after:2012/11/1 before:2012/11/2 is:starred
cd /jawa/pims/www/pub/html/laible/; vi index.html
# as pims on jimmy
cd /misc/yoda/www/plots/sams/laible
mkdir 121f08
ln -s 121f08 121-f08

# AS ROOT ON JAWA, CHECK FOR CSA UPLOADS
ls -alrth /home/jail/home/csa/data

# YMD bash command line
YMD=`date -d "2 days ago" "+year%Y/month%m/day%d"`; echo $YMD

# THIS REPLACES SPACES WITH UNDERSCORES (NOTE ESCAPE CHAR BEFORE SPACE)
find /tmp/valentine -type f -name "*.dat" | rename 's/\ /_/g'

# THIS REPLACES UNDERSCORE-DASH-UNDERSCORE WITH UNDERSCORE
find /tmp/valentine -type f -name "*.dat" | rename 's/_-_/_/g'

# REPOS LOOK AT omlab on jimmy
svn list file:///home/pims/repositories/omlab/mtbi/trunk

# REPOS LOOK AT stroke on jimmy
svn list file:///home/pims/repositories/stroke

# FIND MMA DATA THAT ALSO HAS 121f05 DATA
for i in $( find /misc/yoda/pub/pad/year2012 -maxdepth 3 -type d -name "mma*" ); do b=`dirname ${i}`; find ${b} -maxdepth 1 -type d -name sams2_accel_121f05; done

# SED TRICK
sed ':a;N;$!ba;s/\n/ /g' file
# :a create a label 'a'
# N append the next line to the pattern space
# $! if not the last line, ba branch (go to) label 'a'
# s substitute, /\n/ regex for new line, / / by a space, /g global match (as many times as it can)
# *** sed will loop through step 1 to 3 until it reach the last line, getting all lines fit in the pattern space where sed will substitute all \n characters

# packetWriter GUI on jimmy : GET source from svn://cartman/pims/trunk

# 4 Steps to recursively find and replace in svn exported files; do this starting "here" [at dot] and below:
1. svn export to /tmp/path; cd /tmp/path
2. for i in $(grep -irl _PASSWD .); do sed -i -e 's/_PASSWD/PPW/g' ${i}; done
3. for i in $(grep -irl PASSWD .); do sed -i -e 's/PASSWD/SPW/g' ${i}; done
4. mv entire directory /tmp/path to place you need to work from

# set time [ as root? ]
export http_proxy="http://localhost:31280";  date -s "$(wget -S --spider "http://www.google.com/" 2>&1 | grep -E '^[[:space:]]*[dD]ate:' | sed 's/^[[:space:]]*[dD]ate:[[:space:]]*//')"

# pdfjam extract pages
pdfjam --landscape <input file> <page ranges> -o <output file>
pdfjam --landscape FILE 3,67-70,80 -o out.pdf

# gap detect (mysql host/tables) : you have to modify gapdetect.py for GMT range and timedelta step duration
f=/tmp/gap.csv; echo "gmt,pct,sensor" > ${f}; ~/dev/programs/python/realtime/gapdetect.py >> ${f}; ~/recipes/recipes_pivot_example.py ${f}

# PAD depthfinder
find /misc/yoda/pub/pad/year2013/month07 -maxdepth 2 -type d -regextype sed -regex ".*/.ams.*_accel_121f0."
find /misc/yoda/pub/pad/year2013/month07 -maxdepth 2 -type d -regextype sed -regex ".*/.ams.*_accel_121f08"

# Gap detect
f=/tmp/gap.csv; echo "gmt,pct,sensor" > ${f}; ~/dev/programs/python/realtime/gapdetect.py >> ${f}; ~/recipes/recipes_pivot_example.py ${f}

# Tabular show roadmap PDFs population (using recipes_fileutils.py)
# Build pivot table from start, stop, and pattern inputs shows pop. of roadmap PDFs
 d = datetime.date(2013,7,1)
 dStop = datetime.date(2013,8,5)
 pattern = '.*_121f0\d{1}one_.*roadmaps.*\.pdf$' # '.*roadmaps.*\.pdf$'
 demo_build_pivot_roadmap_pdfs(d, dStop, pattern)

# ssh ike cmd
ssh ike "/usr/local/bin/matlab -nojvm -nosplash -display :0.0 -r \"cd /home/pims/dev/work;startup;x='one';disp(x),quit\""

# (use xpra on ike) example to backfill cutoff roadmaps for MMA:
for M in {4..1}; do pad4roadmapaccounting.bash 2013 ${M} mma_accel_* _spgs_roadmaps*.pdf | grep '^n=0' | sort -rn | transmogrify.py roadmapCutoff; done

# PAD profiles
find /misc/yoda/pub/pad -maxdepth 2 -type f -name "201*_padprofile.jpg" | sort

# update SAMS sensors on ISS table
scp SAMS_Sensors_on_ISS.pdf khrovat@jawa:/tmp # FROM JIMMY
sudo mv /tmp/SAMS_Sensors_on_ISS.pdf /jawa/pims/www/pub/html/ # ON JAWA

# tee pipe
mkfifo pipe && (cat pipe | (COMMAND 1) &) && echo 'test' | tee pipe | (COMMAND 2) && rm pipe

# tee pipe example
mkfifo pipe && (cat pipe | grep yoda &) && df -h | tee pipe | awk 'NR>1{exit};1' && rm pipe

# check packetWriters
for H in $TSCCOMPUTERS; do ssh ${H} pgrep -fl packetWriter; done

# a line in crontab to check mem usage
#*/15 * * * *  top -b -n1 -c -p $(pgrep -d',' -f packetReaderThreadGui) >> /tmp/top.txt


# python unpack tuple or list format print
L = list(txyzTuple); L.insert(0, unix2dtm(txyzTuple[0])); L.insert(0, len(data)); self.log.debug( "CSV {:d},{:},{:f},{:f},{:f},{:f}".format(*L) )
