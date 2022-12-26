import MyAdmin from "./admin";
import {AppParams} from "./admin/types";

const App = (appParams: AppParams) => <MyAdmin {... appParams} />;

export default App;
