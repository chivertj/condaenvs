#conda init bash
#source ${CONDA_PREFIX}/etc/profile.d/conda.sh
source activate base
for env in $(conda env list | cut -d" " -f1); do 
   if [[ ${env:0:1} == "#" ]] ; then continue; fi;
   #conda env export -n $env > ${env}.yml
   echo ${env}
   conda activate ${env}
   version=$(python -V 2>&1 | grep -Po '(?<=Python )(.+)')
   if [[ "$version" ]]
   then
       majorminor=$(python -c "import platform; major, minor, patch = platform.python_version_tuple(); print (major+'.'+minor)")
       wait
       echo ${env}","${majorminor}
       conda deactivate
       conda activate
       wait
       whereis python
       python generateenvcmdupdate3.py --env_current ${env} --no_version --python_version ${majorminor} --env_name ${env}
       wait
       mv environment.yml ${env}_env.yml
       wait
   else
       conda deactivate       
   fi
   

done
