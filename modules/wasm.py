import glob
import os
import shutil
import tarfile
from shutil import copyfile
from subprocess import check_call

import modules.config as c
import modules.functions as f


def run_task_build_pdfium():
    f.debug("Building PDFium...")

    target = "linux"
    build_dir = os.path.join("build", target)
    f.create_dir(build_dir)

    target_dir = os.path.join(build_dir, "pdfium")
    f.remove_dir(target_dir)

    cwd = build_dir
    command = " ".join(
        [
            "gclient",
            "config",
            "--unmanaged",
            "https://pdfium.googlesource.com/pdfium.git",
        ]
    )
    check_call(command, cwd=cwd, shell=True)

    cwd = build_dir
    command = " ".join(["gclient", "sync"])
    check_call(command, cwd=cwd, shell=True)

    cwd = target_dir
    command = " ".join(["git", "checkout", c.pdfium_git_commit])
    check_call(command, cwd=cwd, shell=True)


def run_task_patch():
    f.debug("Patching...")

    source_dir = os.path.join("build", "linux", "pdfium")

    # build config
    source_file = os.path.join(
        source_dir,
        "build",
        "build_config.h",
    )
    if f.file_line_has_content(
        source_file,
        201,
        "#error Please add support for your architecture in build/build_config.h\n",
    ):
        f.replace_line_in_file(
            source_file,
            201,
            "#define ARCH_CPU_X86_FAMILY 1\n#define ARCH_CPU_32_BITS 1\n#define ARCH_CPU_LITTLE_ENDIAN 1\n",
        )

        f.debug("Applied: build config")
    else:
        f.debug("Skipped: build config")

    # compiler thin archive
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "BUILDCONFIG.gn",
    )
    if f.file_line_has_content(
        source_file,
        342,
        '  "//build/config/compiler:thin_archive",\n',
    ):
        f.replace_line_in_file(
            source_file,
            342,
            '  #"//build/config/compiler:thin_archive",\n',
        )

        f.debug("Applied: compiler thin archive")
    else:
        f.debug("Skipped: compiler thin archive")

    # build thin archive
    source_file = os.path.join(
        source_dir,
        "BUILD.gn",
    )
    if f.file_line_has_content(
        source_file,
        203,
        '    configs -= [ "//build/config/compiler:thin_archive" ]\n',
    ):
        f.replace_line_in_file(
            source_file,
            203,
            '    #configs -= [ "//build/config/compiler:thin_archive" ]\n',
        )

        f.debug("Applied: build thin archive")
    else:
        f.debug("Skipped: build thin archive")

    # compiler
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "compiler",
        "BUILD.gn",
    )
    if f.file_line_has_content(
        source_file,
        768,
        '        "-m64",\n',
    ):
        f.replace_line_in_file(
            source_file,
            768,
            '        #"-m64",\n',
        )
        f.replace_line_in_file(
            source_file,
            769,
            '        #"-march=$x64_arch",\n',
        )
        f.replace_line_in_file(
            source_file,
            770,
            '        #"-msse3",\n',
        )

        f.debug("Applied: compiler")
    else:
        f.debug("Skipped: compiler")

    # pragma optimize
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "compiler",
        "BUILD.gn",
    )
    if f.file_line_has_content(
        source_file,
        1541,
        '          "-Wno-ignored-pragma-optimize",\n',
    ):
        f.replace_line_in_file(
            source_file,
            1541,
            '          "-Wno-deprecated-register",\n',
        )

        f.debug("Applied: pragma optimize")
    else:
        f.debug("Skipped: pragma optimize")

    # pubnames
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "compiler",
        "BUILD.gn",
    )
    if f.file_line_has_content(
        source_file,
        2358,
        '        cflags += [ "-ggnu-pubnames" ]\n',
    ):
        f.replace_line_in_file(
            source_file,
            2358,
            '        #cflags += [ "-ggnu-pubnames" ]\n',
        )

        f.debug("Applied: pubnames")
    else:
        f.debug("Skipped: pubnames")

    # gcc toolchain
    source_file = os.path.join(
        source_dir,
        "build",
        "toolchain",
        "gcc_toolchain.gni",
    )
    if f.file_line_has_content(
        source_file,
        643,
        '    cc = "$prefix/clang"\n',
    ):
        f.replace_line_in_file(
            source_file,
            643,
            '    cc = "emcc"\n',
        )
        f.replace_line_in_file(
            source_file,
            644,
            '    cxx = "em++"\n',
        )

        f.debug("Applied: gcc toolchain")
    else:
        f.debug("Skipped: gcc toolchain")

    # partition allocator
    source_file = os.path.join(
        source_dir,
        "third_party",
        "base",
        "allocator",
        "partition_allocator",
        "spin_lock.cc",
    )
    if f.file_line_has_content(
        source_file,
        54,
        '#warning "Processor yield not supported on this architecture."\n',
    ):
        f.replace_line_in_file(
            source_file,
            54,
            '//#warning "Processor yield not supported on this architecture."\n',
        )

        f.debug("Applied: partition allocator")
    else:
        f.debug("Skipped: partition allocator")

    # compiler stack protector
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "compiler",
        "BUILD.gn",
    )
    if f.file_line_has_content(
        source_file,
        306,
        '        cflags += [ "-fstack-protector" ]\n',
    ):
        f.replace_line_in_file(
            source_file,
            306,
            '        cflags += [ "-fno-stack-protector" ]\n',
        )

        f.debug("Applied: compiler stack protector")
    else:
        f.debug("Skipped: compiler stack protector")

    # copy files required
    f.debug("Copying required files...")

    linux_dir = os.path.join(source_dir, "linux")
    f.create_dir(linux_dir)

    f.copyfile("/usr/include/jpeglib.h", os.path.join(source_dir, "jpeglib.h"))
    f.copyfile("/usr/include/jmorecfg.h", os.path.join(source_dir, "jmorecfg.h"))
    f.copyfile("/usr/include/zlib.h", os.path.join(source_dir, "zlib.h"))
    f.copyfile("/usr/include/zconf.h", os.path.join(source_dir, "zconf.h"))
    f.copyfile("/usr/include/jerror.h", os.path.join(source_dir, "jerror.h"))
    f.copyfile(
        "/usr/include/x86_64-linux-gnu/jconfig.h", os.path.join(source_dir, "jconfig.h")
    )
    f.copyfile("/usr/include/linux/limits.h", os.path.join(linux_dir, "limits.h"))

    f.debug("Copied!")


def run_task_build():
    f.debug("Building libraries...")

    current_dir = os.getcwd()

    # configs
    for config in c.configurations_wasm:
        # targets
        for target in c.targets_wasm:
            main_dir = os.path.join(
                "build",
                target["target_os"],
                "pdfium",
                "out",
                "{0}-{1}-{2}".format(target["target_os"], target["target_cpu"], config),
            )

            f.remove_dir(main_dir)
            f.create_dir(main_dir)

            os.chdir(
                os.path.join(
                    "build",
                    target["target_os"],
                    "pdfium",
                )
            )

            # generating files...
            f.debug(
                'Generating files to arch "{0}" and configuration "{1}"...'.format(
                    target["target_cpu"], config
                )
            )

            arg_is_debug = "true" if config == "debug" else "false"

            args = []
            args.append('target_os="{0}"'.format(target["pdfium_os"]))
            args.append('target_cpu="{0}"'.format(target["target_cpu"]))
            args.append("use_goma=false")
            args.append("is_debug={0}".format(arg_is_debug))
            args.append("pdf_use_skia=false")
            args.append("pdf_use_skia_paths=false")
            args.append("pdf_enable_xfa=false")
            args.append("pdf_enable_v8=false")
            args.append("is_component_build=false")
            args.append("clang_use_chrome_plugins=false")
            args.append("pdf_is_standalone=true")
            args.append("use_debug_fission=false")
            args.append("use_custom_libcxx=false")
            args.append("use_sysroot=false")
            args.append("use_system_libjpeg=true")
            args.append("use_system_zlib=true")
            args.append("pdf_is_complete_lib=true")

            if config == "release":
                args.append("symbol_level=0")

            args_str = " ".join(args)

            command = " ".join(
                [
                    "gn",
                    "gen",
                    "out/{0}-{1}-{2}".format(
                        target["target_os"], target["target_cpu"], config
                    ),
                    "--args='{0}'".format(args_str),
                ]
            )
            check_call(command, shell=True)

            # compiling...
            f.debug(
                'Compiling to arch "{0}" and configuration "{1}"...'.format(
                    target["target_cpu"], config
                )
            )

            command = " ".join(
                [
                    "ninja",
                    "-C",
                    "out/{0}-{1}-{2}".format(
                        target["target_os"], target["target_cpu"], config
                    ),
                    "pdfium",
                    "-v",
                ]
            )
            check_call(command, shell=True)

            os.chdir(current_dir)


def run_task_install():
    f.debug("Installing libraries...")

    # configs
    for config in c.configurations_wasm:
        for target in c.targets_wasm:
            f.remove_dir(
                os.path.join("build", target["target_os"], target["target_cpu"], config)
            )

            f.create_dir(
                os.path.join("build", target["target_os"], target["target_cpu"], config)
            )

            source_lib_path = os.path.join(
                "build",
                target["target_os"],
                "pdfium",
                "out",
                "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
                "obj",
                "libpdfium.a",
            )

            target_lib_path = os.path.join(
                "build",
                target["target_os"],
                target["target_cpu"],
                config,
                "libpdfium.a",
            )

            f.copyfile(source_lib_path, target_lib_path)

            # check file
            f.debug("File data...")
            command = " ".join(["file", target_lib_path])
            check_call(command, shell=True)

            f.debug("File size...")
            command = " ".join(["ls", "-lh ", target_lib_path])
            check_call(command, shell=True)

            # include
            include_dir = os.path.join("build", "linux", "pdfium", "public")
            target_include_dir = os.path.join(
                "build", target["target_os"], target["target_cpu"], config, "include"
            )

            f.remove_dir(target_include_dir)
            f.create_dir(target_include_dir)

            for basename in os.listdir(include_dir):
                if basename.endswith(".h"):
                    pathname = os.path.join(include_dir, basename)

                    if os.path.isfile(pathname):
                        shutil.copy2(pathname, target_include_dir)


def run_task_test():
    f.debug("Testing...")

    current_dir = os.getcwd()
    sample_dir = os.path.join(current_dir, "sample-wasm")
    build_dir = os.path.join(sample_dir, "build")
    final_dir = os.path.join("sample-wasm", "build")

    for config in c.configurations_wasm:
        for target in c.targets_wasm:
            lib_file_out = os.path.join(
                current_dir,
                "build",
                target["target_os"],
                target["target_cpu"],
                config,
                "libpdfium.a",
            )

            include_dir = os.path.join(
                current_dir,
                "build",
                target["target_os"],
                target["target_cpu"],
                config,
                "include",
            )

            f.remove_dir(build_dir)
            f.create_dir(build_dir)

            # build
            command = " ".join(
                [
                    "em++",
                    "-o",
                    "build/index.html",
                    "src/main.cpp",
                    lib_file_out,
                    "-I{0}".format(include_dir),
                    "-s",
                    "DEMANGLE_SUPPORT=1",
                    "-s",
                    "USE_PTHREADS",
                    "-s",
                    "USE_ZLIB=1",
                    "-s",
                    "USE_LIBJPEG=1",
                    "--embed-file",
                    "files/web-assembly.pdf",
                ]
            )
            check_call(command, cwd=sample_dir, shell=True)

            f.debug(
                "Test on browser with: python -m http.server --directory {0}".format(
                    final_dir
                )
            )


def run_task_generate():
    f.debug("Generating...")

    current_dir = os.getcwd()

    for config in c.configurations_wasm:
        for target in c.targets_wasm:
            # paths
            utils_dir = os.path.join(current_dir, "extras", "wasm", "utils")

            lib_dir = os.path.join(
                current_dir,
                "build",
                target["target_os"],
                target["target_cpu"],
                config,
            )

            gen_dir = os.path.join(
                current_dir,
                "build",
                target["target_os"],
                target["target_cpu"],
                "gen",
            )

            final_dir = os.path.join(
                "build",
                target["target_os"],
                target["target_cpu"],
                "gen",
                "out",
            )

            f.remove_dir(gen_dir)
            f.create_dir(gen_dir)

            # doxygen
            doxygen_file = os.path.join(
                current_dir,
                "extras",
                "wasm",
                "config",
                "Doxyfile",
            )

            command = " ".join(
                [
                    "doxygen",
                    doxygen_file,
                ]
            )
            check_call(command, cwd=gen_dir, shell=True)

            # copy files
            f.copytree(utils_dir, os.path.join(gen_dir, "utils"))

            # prepare files
            rsp_file = os.path.join(gen_dir, "utils", "pdfium.rsp")
            f.replace_in_file(rsp_file, "{LIB_DIR}", lib_dir)

            # node modules
            gen_utils_dir = os.path.join(
                gen_dir,
                "utils",
            )

            command = " ".join(
                [
                    "npm",
                    "install",
                ]
            )
            check_call(command, cwd=gen_utils_dir, shell=True)

            # generate
            gen_out_dir = os.path.join(
                gen_dir,
                "out",
            )

            f.remove_dir(gen_out_dir)
            f.create_dir(gen_out_dir)

            html_file = os.path.join(
                gen_out_dir,
                "pdfium.html",
            )

            command = " ".join(
                [
                    "emcc",
                    "-o",
                    html_file,
                    "-s",
                    'EXPORTED_FUNCTIONS="$(node function-names ../xml/index.xml createDocFromBuffer)"',
                    "-s",
                    'EXTRA_EXPORTED_RUNTIME_METHODS=\'["ccall", "cwrap"]\'',
                    "--pre-js pre-js.js",
                    "avail.c",
                    "@pdfium.rsp",
                    "-Os",
                ]
            )
            check_call(command, cwd=gen_utils_dir, shell=True)

            # copy files
            node_dir = os.path.join(lib_dir, "node")

            f.remove_dir(node_dir)

            f.copytree(gen_out_dir, node_dir)

            # test
            f.debug(
                "Test on browser with: python -m http.server --directory {0}".format(
                    final_dir
                )
            )

    f.debug("Generated")


def run_task_archive():
    f.debug("Archiving...")

    current_dir = os.getcwd()
    output_filename = os.path.join(current_dir, "wasm.tgz")

    tar = tarfile.open(output_filename, "w:gz")

    for config in c.configurations_wasm:
        for target in c.targets_wasm:
            lib_dir = os.path.join(
                current_dir, "build", target["target_os"], target["target_cpu"], config
            )

            tar.add(
                name=lib_dir,
                arcname=os.path.basename(lib_dir),
                filter=lambda x: (
                    None if "_" in x.name and not x.name.endswith(".h") else x
                ),
            )

    tar.close()
