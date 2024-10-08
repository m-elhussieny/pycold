# Setup basic python stuff and ensure we have skbuild

option(BUILD_PYCOLD "Enable _colds_cython module" TRUE)
if (BUILD_PYCOLD)

  set(cython_source "_colds_cython.pyx")
  set(PYCOLD_MODULE_NAME "_colds_cython")

  # Translate Cython into C/C++
  add_cython_target(${PYCOLD_MODULE_NAME} "${cython_source}" C OUTPUT_VAR sources)

  # Add other C sources
  list(APPEND sources )

  # Create C++ library. Specify include dirs and link libs as normal
  add_library(${PYCOLD_MODULE_NAME} MODULE ${sources})
  target_include_directories(
    ${PYCOLD_MODULE_NAME}
    PUBLIC
        ${NumPy_INCLUDE_DIRS}
        ${PYTHON_INCLUDE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}
  )

  # TODO: not sure why this isn't set in the global scope?
  # Hack around it: just hard code the module name
  set(SCCD_MODULE_NAME "sccd")

  # TODO: linking to the SCCD shared object isn't working 100% yet.


  target_link_libraries(${PYCOLD_MODULE_NAME} ${SCCD_MODULE_NAME} GLMnet)
  
  
  target_compile_definitions(${PYCOLD_MODULE_NAME} PUBLIC
    "NPY_NO_DEPRECATED_API"
    #"NPY_1_7_API_VERSION=0x00000007"
    )

  # Transform the C++ library into an importable python module
  python_extension_module(${PYCOLD_MODULE_NAME})
  if(WIN32)  
    if(MSYS)
      message(STATUS "MSYS2 detected")
    else()# display error and exit
      message(FATAL_ERROR "Currently only MSYS2 is supported for Windows builds.")
    endif()

    target_compile_definitions(${PYCOLD_MODULE_NAME} PRIVATE MS_WIN64=1)# if on windows, add compile definition MS_WIN64=1
    set_target_properties(${SCCD_MODULE_NAME} PROPERTIES INTERFACE_LINK_LIBRARIES "")
    # print LINK_LIBRARIES of target ${PYCOLD_MODULE_NAME}


    set(CMAKE_FIND_LIBRARY_SUFFIXES .a ${CMAKE_FIND_LIBRARY_SUFFIXES})# force use static libs, e.g. libxx.a rather than libxx.dll.a
    find_library(gfortran NAMES gfortran REQUIRED)
    find_library(winpthread NAMES winpthread REQUIRED)
    find_library(quadmath NAMES quadmath REQUIRED)
    find_package(GSL REQUIRED)
    target_link_libraries(${PYCOLD_MODULE_NAME}
    # -Wl,-Bstatic
    ${gfortran} 
    ${winpthread}
    ${quadmath}
    GSL::gsl
    GSL::gslcblas
    -static-libgcc
    ) 

    # HACK: There's no way to remove -lgcc_s inside CMake, so we need to modify it manually
    # Define the path to the linkLibs.rsp file
    set(LINKLIBS_RSP_FILE "${CMAKE_BINARY_DIR}/src/python/pycold/CMakeFiles/${PYCOLD_MODULE_NAME}.dir/linkLibs.rsp")

    # # Custom command to remove -lgcc_s from linkLibs.rsp using sed
    add_custom_command(
        TARGET ${PYCOLD_MODULE_NAME}
        PRE_LINK
        COMMAND sed -i "s/-lgcc_s//g" ${LINKLIBS_RSP_FILE} 
        COMMAND ${CMAKE_COMMAND} -E echo "after removing:"       
        COMMAND ${CMAKE_COMMAND} -E cat ${LINKLIBS_RSP_FILE}
        COMMENT "Removing -lgcc_s from ${TARGET_NAME} linkLibs.rsp"
    )

  endif()
  
  # Install the C++ module to the correct relative location
  # (this will be an inplace build if you use `pip install -e`)
  #file(RELATIVE_PATH pycold_install_dest "${CMAKE_SOURCE_DIR}" "${CMAKE_CURRENT_SOURCE_DIR}")

  # My "normal" method of setting install targets does not seem to work here. Hacking it.
  # NOTE: skbuild *seems* to place libraries in a data dir *unless* the install destination
  # corresponds exactly to the <package_dir>/<package_name> specified implicitly in setup.py
  set(pycold_install_dest "src/python/pycold")

  #install(TARGETS ${SCCD_MODULE_NAME} LIBRARY DESTINATION "${pycold_install_dest}")
  install(TARGETS ${PYCOLD_MODULE_NAME} LIBRARY DESTINATION "${pycold_install_dest}")

endif()
