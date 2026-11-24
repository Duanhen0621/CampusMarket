<template>
  <div>
    <el-upload
      v-model:file-list="fileList"
      list-type="picture-card"
      :auto-upload="false"
      :limit="limit"
      accept="image/*"
      :on-change="handleChange"
      :on-remove="handleChange"
      :on-exceed="handleExceed"
    >
      <span class="upload-plus">+</span>
    </el-upload>
    <div class="muted">
      支持 JPG / PNG / WebP，单张不超过 5MB；上传后自动压缩并返回 URL。
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  limit: { type: Number, default: 9 },
})

const emit = defineEmits(['update:modelValue'])

const fileList = ref([])

watch(
  () => props.modelValue,
  (value) => {
    fileList.value = Array.isArray(value) ? value : []
  },
)

function handleChange(file, files) {
  if (file.size && file.size > 5 * 1024 * 1024) {
    ElMessage.warning('单张图片不能超过 5MB')
    fileList.value = fileList.value.filter((item) => item.uid !== file.uid)
    files = fileList.value
  }
  emit('update:modelValue', files)
}

function handleExceed() {
  ElMessage.warning(`最多上传 ${props.limit} 张图片`)
}
</script>

<style scoped>
.upload-plus {
  font-size: 28px;
  color: #909399;
  line-height: 1;
}
</style>
