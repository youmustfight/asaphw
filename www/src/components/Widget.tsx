import axios from 'axios';
import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { countryCodes } from '../data/countryCodes';
import { TMemberID, fetchMemberIds, generateMemberId, setupSQLiteDatabaseTables, validateMemberId } from '../data/requests';

enum WidgetMode {
  GENERATE = 'generate',
  VALIDATE = 'validate',
}

export const Widget = () => {
  // SETUP
  const [mode, setMode]  = useState(WidgetMode.VALIDATE)
  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null);
  const [memberIds, setMemberIds] = useState<TMemberID[]>([]);
  const clearMessages = () => setFeedbackMessage(null);
  const changeMode = (newMode: WidgetMode) => {
    clearMessages();
    setMode(newMode);
  }

  // --- Generate Handlers/State
  const submitNewId = (firstName: string, lastName: string, dateOfBirth: string, countryCode: string) => {
    clearMessages();
    generateMemberId({ firstName, lastName, dateOfBirth, countryCode })
      .then(() => {
        setFeedbackMessage('Member ID Generated!');
        fetchMemberIds().then((memberIds) => setMemberIds(memberIds))
      })
      .catch(err => setFeedbackMessage(`Error: ${err.response.data.error}`))
  }

  // --- Validation Handlers/State
  const sumbitValidation = (memberId: string) => {
    clearMessages();
    validateMemberId(memberId)
      .then(({ data }) => {
        const statements = []
        // setup message if valid/in use or not valid/reason
        if (data.data.is_valid) {
          statements.push('Member ID is valid.')
          if (data.data.is_registered) statements.push('Member ID is in use.')
        } else {
          statements.push('Member ID is not valid.')
          if (data.data.invalid_reason) statements.push(data.data.invalid_reason)
        }
        setFeedbackMessage(statements.join(' '))
      })
      .catch(err => setFeedbackMessage(`Error: ${err.response.data.error}`))
  }

  // ON MOUNT (just fetch any ids in the database)
  useEffect(() => {
    fetchMemberIds().then((memberIds) => setMemberIds(memberIds))
  }, [])
  
  // RENDER (TODO: break these out into components prob)
  return (
    <>
      <StyledWidget>
        {/* SELECT MODE */}
        <div className="form-options">
          <button className={mode === WidgetMode.VALIDATE ? 'active' : ''} onClick={() => changeMode(WidgetMode.VALIDATE)} data-test-id="widget-validate-btn">Validate</button>
          <button className={mode === WidgetMode.GENERATE ? 'active' : ''} onClick={() => changeMode(WidgetMode.GENERATE)} data-test-id="widget-generate-btn">Generate</button>
        </div>

        {/* GENERATE */}
        {mode === WidgetMode.GENERATE && (
          <form onSubmit={(e) => {
            e.preventDefault();
            // @ts-expect-error
            submitNewId(e.target.firstName.value, e.target.lastName.value, e.target.dob.value, e.target.country.value)
          }}>
            <div className="inputs">
              <label>
                Name
                <div className="row">
                  <input type="text" name="firstName" placeholder="First Name" onChange={clearMessages} data-test-id="member-id-generating-first-name-input" />
                  <input type="text" name="lastName" placeholder="Last Name" onChange={clearMessages} data-test-id="member-id-generating-last-name-input" />
                  </div>
              </label>
              <label>
                Date of Birth
                <input type="date" name="dob" onChange={clearMessages} data-test-id="member-id-generating-dob-input" />
              </label>
              <label>
                Country
                <select name="country" onChange={clearMessages} data-test-id="member-id-generating-country-select">
                  <option value="">---</option>
                  {Object.entries(countryCodes).map(([code, name]) => (
                    <option key={code} value={code}>{code} - {name}</option>
                  ))}
                </select>
              </label>
            </div>
            <button type="submit" data-test-id="member-id-generating-submit">Generate Member ID</button>
            {feedbackMessage && <small data-test-id="feedback-message-small">{feedbackMessage}</small>}
          </form>
        )}
        
        {/* VALIDATE */}
        {mode === WidgetMode.VALIDATE && (
          <form onSubmit={(e) => {
            e.preventDefault();
            // @ts-expect-error
            sumbitValidation(e.target.memberId.value);
          }}>
            <div className="inputs">
              <label data-test-id="member-id-validation-input">
                Member ID
                <input type="text" name="memberId" placeholder="XX-XX-XX-XX-XXXX" onChange={clearMessages} />
              </label>
            </div>
            <button type="submit" data-test-id="member-id-validation-submit">Validate Member ID</button>
            {feedbackMessage && <small data-test-id="feedback-message-small">{feedbackMessage}</small>}
          </form>
        )}
      </StyledWidget>

      {/* FEEDBACK ON MEMBER IDS GENERATED */}
      <StyledMemberIDList>
        <div className='header'>
          <b>Member ID List</b>
          <button onClick={() => setupSQLiteDatabaseTables()} data-test-id="setup-sqlite-database-tables">Init/Reset Database Tables</button>
        </div>
        <div>
          <ul data-test-id="member-id-list-ul">
            {memberIds.map(({ value, created_at }) => (
              <li key={value}>{value}</li>
            ))}
          </ul>
        </div>
      </StyledMemberIDList>
    </>
  )
}

const StyledWidget = styled.div`
  margin: 0 auto;
  margin-top: 4em;
  width: 100%;
  max-width: 480px;

  div.form-options {
    display: flex;
    button {
      flex-grow: 1;
      &.active {
        font-weight: 900;
      }
    }
  }
  
  form {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 12px;
    margin: 0;
    background: #f5f5f5;
    box-shadow: rgb(50 50 223 / 15%) 0px 20px 20px -20px, rgb(0 0 0 / 10%) 0px 30px 60px -30px;
    height: 100%;
    .inputs {
      display: flex;
      flex-direction: column;
      label {
        width: 100%;
        display: flex;
        flex-direction: column;
        margin: 4px 0 8px;
      }
      input, select {
        min-height: 32px; 
        margin-top: 4px;
      }
    }
    & > button {
      margin-top: 1em;
      margin-bottom: 0.5em;
    }
    & > small {
      text-align: center;
    }
  }

  .row {
    display: flex;
    & > * {
      flex-grow: 1;
    }
  }
`;

const StyledMemberIDList = styled.div`
  margin: 0 auto;
  margin-top: 4em;
  max-width: 480px;
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    border-bottom: 2px solid #eaeaea;
    button {
      height: 24px;
    }
  }
`;
