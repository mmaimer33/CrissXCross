import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {

  const [data, setData] = useState([{}]);

  useEffect(()=>{
    axios.get('http://localhost:5000/test').then(response => {
      console.log("SUCCESS", response)
      setData(response)
    }).catch(error => {
      console.log(error)
    })

  }, [])

  class testForm extends React.Component {
    render() {
      return (
        <div>
          <h3>Add task</h3>
          <form>
            <label>
              Task
              <input style={{ margin: "0 1rem" }} type="text" value={""} />
            </label>
          </form>
        </div>
      )
    }
  }

  return (
    <div className="App">
      <header className="App-header">
        <h2>CrissXCross</h2>
        <div>{data.status === 200 ? 
          <div>
            <h3>{data.data.messages.map(
              message => <p>{message}</p>
            )}</h3>
            <testForm>{testForm}</testForm>
          </div>
          :
          <h3>LOADING</h3>}</div>
      </header>
    </div>
  );
}

export default App;