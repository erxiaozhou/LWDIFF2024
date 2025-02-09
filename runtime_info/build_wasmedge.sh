export CC=/usr/bin/clang
export CXX=/usr/bin/clang++

current_path=$(pwd)
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
install_dir="$script_dir/install"
mkdir -p "$install_dir"

rm -rf build ; mkdir build ; 
cd build ; cmake  -DCMAKE_INSTALL_PREFIX="$install_dir"  -DCMAKE_BUILD_TYPE=Release -DWASMEDGE_BUILD_AOT_RUNTIME=OFF .. 
make -j
make install
cd ..
rm -rf build
