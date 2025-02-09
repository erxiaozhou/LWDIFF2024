export CC=/usr/lib/llvm-16/bin/clang
export CXX=/usr/lib/llvm-16/bin/clang++
current_path=$(pwd)
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
install_dir="$script_dir/install_jit"
mkdir -p "$install_dir"
cd "$script_dir/product-mini/platforms/linux/";rm -rf build
cmake  -DWAMR_BUILD_AOT=1 -DWAMR_BUILD_JIT=1 -DWAMR_BUILD_FAST_JIT=0   -DCMAKE_INSTALL_PREFIX="$install_dir" -DWAMR_BUILD_REF_TYPES=1 -DCMAKE_BUILD_TYPE=Release  -DWASM_ENABLE_BULK_MEMORY=1 -DWAMR_BUILD_LIBC_WASI=0 -DWAMR_BUILD_LIBC_BUILTIN=1 -DWAMR_BUILD_SIMD=1 -Bbuild
cd build
make -j40
make install
cd ..
rm -rf build
cd "$current_path"