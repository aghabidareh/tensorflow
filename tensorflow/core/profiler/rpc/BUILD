load("//tensorflow:tensorflow.default.bzl", "tf_external_workspace_visible", "tf_grpc_cc_dependencies")
load("//tensorflow/core/platform:rules_cc.bzl", "cc_library")
load(
    "//tensorflow/core/profiler/builds:build_config.bzl",
    "tf_profiler_alias",
    "tf_profiler_copts",
    "tf_profiler_pybind_cc_library_wrapper",
)

package(
    # copybara:uncomment default_applicable_licenses = ["//tensorflow:license"],
    default_visibility = ["//tensorflow/core/profiler:internal"],
    licenses = ["notice"],
)

cc_library(
    name = "grpc",
    hdrs = ["grpc.h"],
    deps = [
        tf_profiler_alias("//tensorflow/core/profiler/rpc/", "grpc"),
    ] + tf_grpc_cc_dependencies(),
)

exports_files(
    [
        "grpc.h",
    ],
    visibility = ["//tensorflow/core/profiler/rpc:__subpackages__"],
)

# Linked to pywrap_tensorflow.
cc_library(
    name = "profiler_service_impl",
    hdrs = ["profiler_service_impl.h"],
    copts = tf_profiler_copts(),
    visibility = tf_external_workspace_visible(
        [
            "//tensorflow/core/data/service:__pkg__",
            "//tensorflow/core/distributed_runtime/rpc:__pkg__",
            "//tensorflow_serving/model_servers:__pkg__",
        ],
    ),
    deps = [
        "//tensorflow/core:lib",
        "//tensorflow/core/profiler/lib:profiler_session",
        "//tensorflow/core/profiler/rpc/client:save_profile",
        "//tensorflow/core/profiler/utils:math_utils",
        "//tensorflow/core/profiler/utils:xplane_utils",
        "@com_google_absl//absl/base:core_headers",
        "@com_google_absl//absl/container:flat_hash_map",
        "@com_google_absl//absl/memory",
        "@com_google_absl//absl/strings",
        "@local_tsl//tsl/profiler/protobuf:profiler_service_cc_grpc_proto",
        "@local_tsl//tsl/profiler/protobuf:profiler_service_proto_cc",
        "@local_tsl//tsl/profiler/protobuf:xplane_proto_cc",
        "@local_xla//xla/tsl/profiler/rpc:profiler_service_impl",
        "@local_xla//xla/tsl/profiler/utils:file_system_utils",
        "@local_xla//xla/tsl/profiler/utils:time_utils",
    ] + tf_grpc_cc_dependencies(),
)

tf_profiler_pybind_cc_library_wrapper(
    name = "profiler_server_for_pybind",
    actual = ":profiler_server_impl",
    visibility = [
        "//tensorflow/python/profiler/internal:__pkg__",
        "@org_xprof//xprof/pywrap:__pkg__",
    ],
)

cc_library(
    name = "profiler_server_impl",
    hdrs = ["profiler_server.h"],
    copts = tf_profiler_copts(),
    visibility = [
        "//tensorflow:__pkg__",
        "//tensorflow/core/profiler:internal",
        "//tensorflow/python:__pkg__",
        "//tensorflow/python/profiler/internal:__pkg__",
        "@local_xla//xla:__subpackages__",
        "@local_xla//xla/tsl/profiler/rpc/client:__pkg__",
        "@org_xprof//xprof/pywrap:__pkg__",
    ],
    deps = [
        ":profiler_service_impl",
        "//tensorflow/core:lib",
        "@com_google_absl//absl/base:core_headers",
        "@com_google_absl//absl/strings",
        "@local_tsl//tsl/profiler/protobuf:profiler_service_cc_grpc_proto",
        "@local_xla//xla/tsl/profiler/rpc:profiler_server_impl",
    ] + tf_grpc_cc_dependencies(),
    alwayslink = True,
)
