# 


mode_name=$1
subdir_id=$2
total_num=$3
# param2=$2
batch_num=200000

# python script_gen_prepare_batch_raw_wasm_smith_cmd.py  simd_ensure_term_bm "25b1" 200000 100 101 /media/hdd8T1/inv_wasm_smith/pre_seed 

# 
result=$((total_num / batch_num))
variable=20
#  0  result 
for ((i=0; i<=result; i++))
do
  echo ": $i"
done
