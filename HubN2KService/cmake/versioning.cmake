set(APP_NAME ${CMAKE_PROJECT_NAME}) 
set(TAG_PREFIX "hub-n2kcore")

function(extract_version_from_git)
    find_package(Git QUIET)
    if(NOT GIT_FOUND)
        set(GIT_VERSION "0.0.0-nogit" PARENT_SCOPE)
        message(WARNING "Git not found, using fallback version for ${APP_NAME}")
        return()
    endif()

    # Check if we're in a git repository
    execute_process(
        COMMAND ${GIT_EXECUTABLE} rev-parse --git-dir
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        RESULT_VARIABLE GIT_RESULT
        OUTPUT_QUIET
        ERROR_QUIET
    )
    
    if(NOT GIT_RESULT EQUAL 0)
        set(GIT_VERSION "0.0.0-notgit" PARENT_SCOPE)
        message(WARNING "Not in git repository, using fallback version for ${APP_NAME}")
        return()
    endif()

    # Get all tags matching our prefix, sorted by version (newest first)
    execute_process(
        COMMAND ${GIT_EXECUTABLE} tag -l "${TAG_PREFIX}-v*" --sort=-version:refname
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        OUTPUT_VARIABLE APP_TAGS
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
    )

    if(NOT APP_TAGS)
        # No tags found, use commit-based version
        execute_process(
            COMMAND ${GIT_EXECUTABLE} rev-list --count HEAD
            WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
            OUTPUT_VARIABLE COMMIT_COUNT
            OUTPUT_STRIP_TRAILING_WHITESPACE
        )
        
        execute_process(
            COMMAND ${GIT_EXECUTABLE} rev-parse --short HEAD
            WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
            OUTPUT_VARIABLE COMMIT_HASH
            OUTPUT_STRIP_TRAILING_WHITESPACE
        )
        
        set(GIT_VERSION "0.0.0-${COMMIT_COUNT}-g${COMMIT_HASH}" PARENT_SCOPE)
        message(STATUS "${APP_NAME}: No tags found, using commit-based version")
        return()
    endif()

    # Get the latest tag
    string(REPLACE "\n" ";" TAG_LIST ${APP_TAGS})
    list(GET TAG_LIST 0 LATEST_TAG)
    
    # Extract version from tag (remove prefix and 'v')
    string(REGEX REPLACE "^${TAG_PREFIX}-v(.+)$" "\\1" BASE_VERSION ${LATEST_TAG})
    
    # Check if we're exactly at the tagged commit
    execute_process(
        COMMAND ${GIT_EXECUTABLE} describe --exact-match --tags HEAD
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        OUTPUT_VARIABLE EXACT_TAG
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
        RESULT_VARIABLE TAG_EXACT_RESULT
    )
    
    if(TAG_EXACT_RESULT EQUAL 0)
        if(EXACT_TAG STREQUAL LATEST_TAG)
            # Exactly at tagged commit
            set(FULL_VERSION ${BASE_VERSION})
        else()
            # Ahead of tag, add commit info
            execute_process(
                COMMAND ${GIT_EXECUTABLE} rev-list --count ${LATEST_TAG}..HEAD
                WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
                OUTPUT_VARIABLE COMMITS_AHEAD
                OUTPUT_STRIP_TRAILING_WHITESPACE
            )
            
            execute_process(
                COMMAND ${GIT_EXECUTABLE} rev-parse --short HEAD
                WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
                OUTPUT_VARIABLE COMMIT_HASH
                OUTPUT_STRIP_TRAILING_WHITESPACE
            )
            
            # Check for uncommitted changes
            execute_process(
                COMMAND ${GIT_EXECUTABLE} diff-index --quiet HEAD --
                WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
                RESULT_VARIABLE DIRTY_RESULT
            )
            
            set(DIRTY_SUFFIX "")
            if(NOT DIRTY_RESULT EQUAL 0)
                set(DIRTY_SUFFIX "-dirty")
            endif()
            
            if(COMMITS_AHEAD GREATER 0)
                set(FULL_VERSION "${BASE_VERSION}-${COMMITS_AHEAD}-g${COMMIT_HASH}${DIRTY_SUFFIX}")
            else()
                set(FULL_VERSION "${BASE_VERSION}${DIRTY_SUFFIX}")
            endif()
        endif()
    else()
        # Ahead of tag, add commit info
        execute_process(
            COMMAND ${GIT_EXECUTABLE} rev-list --count ${LATEST_TAG}..HEAD
            WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
            OUTPUT_VARIABLE COMMITS_AHEAD
            OUTPUT_STRIP_TRAILING_WHITESPACE
        )
        
        execute_process(
            COMMAND ${GIT_EXECUTABLE} rev-parse --short HEAD
            WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
            OUTPUT_VARIABLE COMMIT_HASH
            OUTPUT_STRIP_TRAILING_WHITESPACE
        )
        
        # Check for uncommitted changes
        execute_process(
            COMMAND ${GIT_EXECUTABLE} diff-index --quiet HEAD --
            WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
            RESULT_VARIABLE DIRTY_RESULT
        )
        
        set(DIRTY_SUFFIX "")
        if(NOT DIRTY_RESULT EQUAL 0)
            set(DIRTY_SUFFIX "-dirty")
        endif()
        
        if(COMMITS_AHEAD GREATER 0)
            set(FULL_VERSION "${BASE_VERSION}-${COMMITS_AHEAD}-g${COMMIT_HASH}${DIRTY_SUFFIX}")
        else()
            set(FULL_VERSION "${BASE_VERSION}${DIRTY_SUFFIX}")
        endif()
    endif()
    
    set(GIT_VERSION ${FULL_VERSION} PARENT_SCOPE)
endfunction()

function(parse_semantic_version VERSION_STRING)
    # Extract major.minor.patch from version string
    string(REGEX MATCH "^([0-9]+)\\.([0-9]+)\\.([0-9]+)" _ ${VERSION_STRING})
    
    if(CMAKE_MATCH_1)
        set(VERSION_MAJOR ${CMAKE_MATCH_1} PARENT_SCOPE)
        set(VERSION_MINOR ${CMAKE_MATCH_2} PARENT_SCOPE)
        set(VERSION_PATCH ${CMAKE_MATCH_3} PARENT_SCOPE)
    else()
        # Fallback for development versions
        set(VERSION_MAJOR 0 PARENT_SCOPE)
        set(VERSION_MINOR 0 PARENT_SCOPE)
        set(VERSION_PATCH 0 PARENT_SCOPE)
    endif()
endfunction()

function(generate_version_header)
    set(VERSION_HEADER_CONTENT
"#ifndef ${APP_NAME}_VERSION_H
#define ${APP_NAME}_VERSION_H

// Version information
#define ${APP_NAME}_VERSION_MAJOR ${VERSION_MAJOR}
#define ${APP_NAME}_VERSION_MINOR ${VERSION_MINOR}
#define ${APP_NAME}_VERSION_PATCH ${VERSION_PATCH}
#define ${APP_NAME}_VERSION_STRING \"${GIT_VERSION}\"

// Convenience macros
#define ${APP_NAME}_VERSION_NUMBER (${VERSION_MAJOR} * 10000 + ${VERSION_MINOR} * 100 + ${VERSION_PATCH})
#define ${APP_NAME}_VERSION_AT_LEAST(major, minor, patch) \\
    (${APP_NAME}_VERSION_NUMBER >= ((major) * 10000 + (minor) * 100 + (patch)))

// Build information
#define ${APP_NAME}_BUILD_DATE \"${BUILD_DATE}\"
#define ${APP_NAME}_BUILD_TIME \"${BUILD_TIME}\"

#ifdef __cplusplus
namespace ${APP_NAME} {
    constexpr int VERSION_MAJOR = ${VERSION_MAJOR}\;
    constexpr int VERSION_MINOR = ${VERSION_MINOR}\;
    constexpr int VERSION_PATCH = ${VERSION_PATCH}\;
    constexpr const char* VERSION_STRING = \"${GIT_VERSION}\"\;
    constexpr const char* BUILD_DATE = \"${BUILD_DATE}\"\;
    constexpr const char* BUILD_TIME = \"${BUILD_TIME}\"\;
}
#endif

#endif // ${APP_NAME}_VERSION_H
")
    
    # Create version header in build directory
    set(VERSION_HEADER_PATH "${CMAKE_CURRENT_BINARY_DIR}/src/${APP_NAME}_version.h")
    file(WRITE ${VERSION_HEADER_PATH} ${VERSION_HEADER_CONTENT})
    
    message(STATUS "${APP_NAME}: Generated version header at ${VERSION_HEADER_PATH}")
endfunction()

# Main execution
message(STATUS "${APP_NAME}: Setting up versioning...")

# Extract version from git
extract_version_from_git()

# Parse version components
parse_semantic_version(${GIT_VERSION})

# Get build timestamp
string(TIMESTAMP BUILD_DATE "%Y-%m-%d")
string(TIMESTAMP BUILD_TIME "%H:%M:%S")

# Generate version header
# file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/src")
generate_version_header()

# Set variables for use in main CMakeLists.txt
set(${APP_NAME}_VERSION ${GIT_VERSION})
set(${APP_NAME}_VERSION_MAJOR ${VERSION_MAJOR})
set(${APP_NAME}_VERSION_MINOR ${VERSION_MINOR})
set(${APP_NAME}_VERSION_PATCH ${VERSION_PATCH})
set(${APP_NAME}_VERSION_HEADER "${CMAKE_CURRENT_BINARY_DIR}/src/${APP_NAME}_version.h")

message(STATUS "${APP_NAME}: Version ${GIT_VERSION} (${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH})")

# Optional: Create version.cpp file for runtime access
set(VERSION_CPP_CONTENT
"// Auto-generated version information for ${APP_NAME}
#include \"${APP_NAME}_version.h\"
#include <string>

namespace ${APP_NAME} {
    const std::string getVersionString() {
        return VERSION_STRING\;
    }
    
    const std::string getBuildInfo() {
        return std::string(BUILD_DATE) + \" \" + std::string(BUILD_TIME)\;
    }
    
    int getVersionMajor() { return VERSION_MAJOR\; }
    int getVersionMinor() { return VERSION_MINOR\; }
    int getVersionPatch() { return VERSION_PATCH\; }
}
")

file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/src/${APP_NAME}_version.cpp" ${VERSION_CPP_CONTENT})
set(${APP_NAME}_VERSION_SOURCE "${CMAKE_CURRENT_BINARY_DIR}/src/${APP_NAME}_version.cpp")