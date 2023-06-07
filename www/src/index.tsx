import React from "react";
import ReactDOM from "react-dom";
import styled from "styled-components";
import { Widget } from "./Widget";

const App: React.FC = () => {
  return (
    <AppForm>
      <Widget />
    </AppForm>
  );
};

const AppForm = styled.div`
  min-height: 100vh;
  min-width: 100vw;
  max-width: 100vw;
  * {
    font-family: 'Comic Sans', sans-serif;
  }
`;

ReactDOM.render(<App />, document.querySelector("#root"));
