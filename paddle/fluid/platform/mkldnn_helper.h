/* Copyright (c) 2017 PaddlePaddle Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License. */
#pragma once

#include <algorithm>
#include <iostream>
#include <memory>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

#include "dnnl.hpp"  // NOLINT
#include "paddle/fluid/framework/operator.h"
#include "paddle/phi/backends/onednn/onednn_helper.h"
#include "paddle/phi/common/place.h"
namespace paddle {
#ifdef PADDLE_WITH_MKLDNN
using phi::OneDNNContext;
#endif
namespace platform {

inline void ClearMKLDNNCache(const platform::Place& place,
                             void* ptr = nullptr) {
  // Clear mkl-dnn cache,
  if (platform::is_cpu_place(place)) {
    platform::DeviceContextPool& pool = platform::DeviceContextPool::Instance();
    OneDNNContext* dev_ctx = reinterpret_cast<OneDNNContext*>(pool.Get(place));
    dev_ctx->ResetBlobMap(ptr);
  }
}

inline void DontClearMKLDNNCache(const platform::Place& place) {
  // Clear mkl-dnn cache,
  if (platform::is_cpu_place(place)) {
    platform::DeviceContextPool& pool = platform::DeviceContextPool::Instance();
    OneDNNContext* dev_ctx = reinterpret_cast<OneDNNContext*>(pool.Get(place));
    dev_ctx->BlockNextCacheClearing();
  }
}

// If MKLDNN build and CPU place then register suffix in DeviceContext
inline void AttachPointerHashToMKLDNNKey(void* ptr,
                                         const platform::Place& place) {
  if (platform::is_cpu_place(place)) {
    // Static vars will remember first executor and its thread
    // so both of them need to be processed by the same thread within
    // critical section
    static std::mutex static_vars_barrier;
    static_vars_barrier.lock();
    static auto first_exec = ptr;
    static auto first_thread = phi::funcs::ThreadIDasStr();
    static_vars_barrier.unlock();

    if (first_exec != ptr) {
      OneDNNContext::tls().set_key_suffix(
          "E" + std::to_string(reinterpret_cast<uintptr_t>(ptr)));
    }
    // Let's register adress of current executor
    OneDNNContext::tls().set_curr_exec(ptr);

    // For first thread
    if (first_thread == phi::funcs::ThreadIDasStr()) {
      OneDNNContext::tls().disable_tid_in_key();
    }
  }
}

inline void RegisterModelLayout(
    std::vector<std::unique_ptr<framework::OperatorBase>>& ops,  // NOLINT
    const platform::Place& place) {
  if (platform::is_cpu_place(place)) {
    // If there is already registered NHWC then quit this call
    // not to overwrite setting with analysis of internal "while" op block
    if (OneDNNContext::tls().get_cur_paddle_data_layout() ==
        phi::DataLayout::kNHWC)
      return;

    VLOG(4) << "RegisterModelLayout for mkldnn";
    auto check_attrib = [](std::unique_ptr<framework::OperatorBase>& op,
                           const std::string& attrib_name) -> bool {
      if (op->HasAttr(attrib_name)) {
        auto data_format = op->Attr<std::string>(attrib_name);
        OneDNNContext::tls().set_cur_paddle_data_layout(
            data_format.compare("NHWC") == 0 ? phi::DataLayout::kNHWC
                                             : phi::DataLayout::kNCHW);
        return true;
      } else {
        return false;
      }
    };

    for (auto& op : ops) {
      if (check_attrib(op, std::string("data_format"))) {
        return;
      }
      if (check_attrib(op, std::string("data_layout"))) {
        return;
      }
    }
  }
}

inline bool HasOpINT8DataType(const paddle::framework::OpDesc* op) {
  return (op->GetAttrIfExists<std::string>("mkldnn_data_type") == "int8" ||
          op->GetAttrIfExists<bool>("use_quantizer"));
}

inline bool HasOpBFLOAT16DataType(const paddle::framework::OpDesc* op) {
  return op->GetAttrIfExists<std::string>("mkldnn_data_type") == "bfloat16";
}

}  // namespace platform

inline std::string FindInputNameByVarName(framework::OpDesc* op,
                                          const std::string& searched_name) {
  std::string ret;
  for (const auto& name : op->InputNames())
    for (const auto& input_name : op->Input(name))
      if (input_name == searched_name) ret = name;
  return ret;
}

inline std::string FindOutputNameByVarName(framework::OpDesc* op,
                                           const std::string& searched_name) {
  std::string ret;
  for (const auto& name : op->OutputNames())
    for (const auto& output_name : op->Output(name))
      if (output_name == searched_name) ret = name;
  return ret;
}
}  // namespace paddle
