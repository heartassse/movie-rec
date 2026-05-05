<template>
  <div class="stars" :class="{ disabled }">
    <button
      v-for="n in 5"
      :key="n"
      class="star"
      :class="{ active: n <= modelValue }"
      type="button"
      @click="onClick(n)"
      :disabled="disabled"
      :aria-label="`评分 ${n} 分`"
    >
      ★
    </button>
  </div>
</template>

<script>
export default {
  name: 'RatingStars',
  props: {
    modelValue: { type: Number, default: 0 },
    disabled: { type: Boolean, default: false },
  },
  emits: ['update:modelValue', 'change'],
  methods: {
    onClick(n) {
      this.$emit('update:modelValue', n)
      this.$emit('change', n)
    },
  },
}
</script>

<style scoped>
.stars {
  display: inline-flex;
  gap: 6px;
}
.star {
  background: transparent;
  border: none;
  font-size: 22px;
  line-height: 1;
  cursor: pointer;
  color: #e8e8e8;
  padding: 0;
  -webkit-text-stroke: 1.2px #bfbfbf;
}
.star.active {
  color: #f6c45a;
  -webkit-text-stroke: 1.2px #d4a02a;
}
.stars.disabled .star {
  cursor: not-allowed;
  opacity: 0.7;
}
</style>
