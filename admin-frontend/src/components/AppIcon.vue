<template>
  <component :is="icon" :size="size" :stroke-width="strokeWidth" class="shrink-0" />
</template>

<script setup>
import { computed } from 'vue'
import {
  LayoutDashboard, Package, Users, BarChart3, UserCheck, ShieldAlert,
  Menu, X, LogOut, LogIn, Clock, Plus, RotateCw, Pencil, Eye, EyeOff,
  ExternalLink, FilterX, ArrowRight, ArrowLeft, CheckCircle2, Ban,
  UserCog, UserPlus, Search, AlertCircle, AlertTriangle, Loader2,
  ShoppingCart, PackageX, ClipboardList, PieChart, FileText, Receipt,
  User, Phone, Lock, Calendar, CalendarDays, AlarmClock, GitBranch,
  Truck, ChevronDown, ChevronLeft, ChevronRight, Armchair, Save,
  Check, Play, Hourglass, Info, Circle, FileBarChart2,
} from 'lucide-vue-next'

const MAP = {
  dashboard:          LayoutDashboard,
  shopping_bag:       Package,
  inventory_2:        Package,
  people:             Users,
  people_outline:     Users,
  bar_chart:          BarChart3,
  badge:              UserCheck,
  troubleshoot:       ShieldAlert,
  menu:               Menu,
  close:              X,
  cancel:             X,
  logout:             LogOut,
  login:              LogIn,
  schedule:           Clock,
  add:                Plus,
  refresh:            RotateCw,
  edit:               Pencil,
  visibility:         Eye,
  visibility_off:     EyeOff,
  open_in_new:        ExternalLink,
  filter_alt_off:     FilterX,
  arrow_forward:      ArrowRight,
  arrow_back:         ArrowLeft,
  check_circle:       CheckCircle2,
  block:              Ban,
  manage_accounts:    UserCog,
  person_add:         UserPlus,
  search:             Search,
  manage_search:      Search,
  error:              AlertCircle,
  error_outline:      AlertCircle,
  warning:            AlertTriangle,
  progress_activity:  Loader2,
  add_shopping_cart:  ShoppingCart,
  shopping_cart_off:  PackageX,
  pending_actions:    ClipboardList,
  donut_large:        PieChart,
  receipt_long:       FileText,
  assignment:         FileText,
  person:             User,
  phone:              Phone,
  lock:               Lock,
  calendar_month:     Calendar,
  calendar_today:     CalendarDays,
  alarm_on:           AlarmClock,
  timeline:           GitBranch,
  local_shipping:     Truck,
  expand_more:        ChevronDown,
  chevron_left:       ChevronLeft,
  chevron_right:      ChevronRight,
  chair:              Armchair,
  save:               Save,
  check:              Check,
  play_arrow:         Play,
  hourglass_empty:    Hourglass,
  info:               Info,
  circle:             Circle,
}

const props = defineProps({
  name: { type: String, required: true },
  size: { type: [Number, String], default: 20 },
  strokeWidth: { type: [Number, String], default: 1.75 },
})

const icon = computed(() => MAP[props.name] || Circle)
</script>
