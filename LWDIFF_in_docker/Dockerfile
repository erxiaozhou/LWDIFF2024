FROM ubuntu:20.04

RUN apt-get update && apt-get install -y \
    sudo \
    curl \
    gnupg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash anonymous && echo 'anonymous:000000' | chpasswd && adduser anonymous sudo


WORKDIR /home/anonymous

RUN echo 'anonymous ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

COPY v19_tcs_from_cloud.tar /home/anonymous/CP912/v19_tcs_from_cloud.tar
COPY runtime_tester.tar /home/anonymous/CP912/runtime_tester.tar

COPY collected_runtimes/iwasm_pg_ori_wamr_install_classic_interpreter /home/anonymous/CP912/iwasm_pg/ori_wamr/install_classic_interpreter
COPY collected_runtimes/iwasm_pg_wamr_classic_install /home/anonymous/CP912/iwasm_pg/wamr_classic/install
COPY collected_runtimes/iwasm_pg_ori_wamr_install_fast_interpreter /home/anonymous/CP912/iwasm_pg/ori_wamr/install_fast_interpreter
COPY collected_runtimes/iwasm_pg_wamr_fast_install /home/anonymous/CP912/iwasm_pg/wamr_fast/install
COPY collected_runtimes/iwasm_pg_ori_wamr_install_mt_jit /home/anonymous/CP912/iwasm_pg/ori_wamr/install_mt_jit
COPY collected_runtimes/iwasm_pg_wamr_mt_jit_install /home/anonymous/CP912/iwasm_pg/wamr_mt_jit/install
COPY collected_runtimes/iwasm_pg_ori_wamr_install_jit /home/anonymous/CP912/iwasm_pg/ori_wamr/install_jit
COPY collected_runtimes/iwasm_pg_wamr_jit_install /home/anonymous/CP912/iwasm_pg/wamr_jit/install
COPY collected_runtimes/iwasm_pg_ori_wamr_install_fast_jit /home/anonymous/CP912/iwasm_pg/ori_wamr/install_fast_jit
COPY collected_runtimes/iwasm_pg_wamr_fast_jit_install /home/anonymous/CP912/iwasm_pg/wamr_fast_jit/install
COPY collected_runtimes/WasmEdge_install /home/anonymous/CP912/WasmEdge/install
COPY collected_runtimes/ld_WasmEdge_disableAOT_lastest_install /home/anonymous/CP912/ld_WasmEdge_disableAOT_lastest/install
COPY collected_runtimes/wasmtime_install /home/anonymous/CP912/wasmtime/install
COPY collected_runtimes/wasmtime /home/anonymous/CP912/wasmtime2/install/bin/wasmtime
COPY collected_runtimes/for_testing_ori_wasmer_lastest_target_release_wasmer /home/anonymous/CP912/for_testing/ori_wasmer_lastest/target/release/wasmer
COPY collected_runtimes/for_testing_ld_wasmer_lastest_target_release_wasmer /home/anonymous/CP912/for_testing/ld_wasmer_lastest/target/release/wasmer
COPY collected_runtimes/iwasm_pg_wamr_cov_v1_install_jit /home/anonymous/CP912/iwasm_pg/wamr_cov_v1/install_jit


RUN mkdir /home/anonymous/CP912/iwasm_pg/wamr_classic/install -p && \
    mkdir /home/anonymous/CP912/iwasm_pg/wamr_fast/install -p && \
    mkdir /home/anonymous/CP912/iwasm_pg/wamr_mt_jit/install -p && \
    mkdir /home/anonymous/CP912/iwasm_pg/wamr_jit/install -p && \
    mkdir /home/anonymous/CP912/iwasm_pg/wamr_fast_jit/install -p && \
    mkdir /home/anonymous/CP912/ld_WasmEdge_disableAOT_lastest/dump_result -p && \
    mkdir /home/anonymous/CP912/wasmtime2 -p && \
    mkdir /home/anonymous/CP912/for_testing/ld_wasmer_lastest -p 

COPY necessary_bin/wasm2wat /home/anonymous/CP912/necessary_bin/wasm2wat
COPY necessary_bin/wat2wasm /home/anonymous/CP912/necessary_bin/wat2wasm
COPY necessary_bin/wasm-validate /home/anonymous/CP912/necessary_bin/wasm-validate
COPY only_nop /home/anonymous/CP912/only_nop


RUN chown -R anonymous:anonymous /home/anonymous
RUN chmod -R 777 /home/anonymous/CP912

RUN tar -xvf /home/anonymous/CP912/runtime_tester.tar -C /home/anonymous/CP912/&& \
    chown -R anonymous:anonymous /home/anonymous/CP912/runtime_tester
USER anonymous

RUN tar -xvf /home/anonymous/CP912/v19_tcs_from_cloud.tar -C /home/anonymous/CP912/

RUN echo 'export PATH=$HOME/CP912/necessary_bin:$PATH' >> ~/.bashrc
RUN curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda && \
    rm Miniconda3-latest-Linux-x86_64.sh && \
    $HOME/miniconda/bin/conda init && \
    echo 'export PATH=$HOME/miniconda/bin:$PATH' >> ~/.bashrc

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    echo 'source $HOME/.cargo/env' >> ~/.bashrc

COPY tester.yml /home/anonymous/tester.yml
RUN /home/anonymous/miniconda/bin/conda env create -f /home/anonymous/tester.yml


USER anonymous
WORKDIR /home/anonymous/CP912/runtime_tester
RUN echo "source /home/anonymous/miniconda/bin/activate tester" >> ~/.bashrc

# RUN echo '#!/bin/bash\nsource /home/anonymous/miniconda/bin/activate tester\nsource /home/anonymous/script_remove_dead_process.sh &\nexec "$@"' > /home/anonymous/start.sh && \

RUN echo '#!/bin/bash\nsource /home/anonymous/miniconda/bin/activate tester\nexec "$@"' > /home/anonymous/start.sh && \
    chmod +x /home/anonymous/start.sh


ENTRYPOINT ["/home/anonymous/start.sh"]
CMD ["bash"]

