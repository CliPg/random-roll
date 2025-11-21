import { createSSRApp } from "vue";
import App from "./App.vue";
import uniIcons from "@dcloudio/uni-ui/lib/uni-icons/uni-icons.vue";

export function createApp() {
  const app = createSSRApp(App);
  app.component("uni-icons", uniIcons);
  return {
    app,
  };
}
