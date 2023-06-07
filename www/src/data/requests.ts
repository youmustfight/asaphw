import axios from 'axios';
import { getServiceApiUrl } from '../env';

// TYPES
export type TMemberID = { value: string, created_at: string }

// REQUESTS
// --- Database
export const setupSQLiteDatabaseTables = () => axios.post('http://localhost:3000/database/init')

// --- Members
export const generateMemberId = ({
  firstName,
  lastName,
  dateOfBirth,
  countryCode,
}: {
  firstName: string,
  lastName: string,
  dateOfBirth: string,
  countryCode: string,
}) => axios
  .post(`${getServiceApiUrl()}/v1/member_id`, {
    first_name: firstName,
    last_name: lastName,
    dob: dateOfBirth,
    country: countryCode,
  })

export const validateMemberId = (memberId: string) => axios
  .post(`${getServiceApiUrl()}/v1/member_id/validate`, {
    member_id: memberId,
  })

export const fetchMemberIds = (): Promise<TMemberID[]> => axios
  .get(`${getServiceApiUrl()}/v1/member_ids`)
  .then(res => res.data.data.member_ids)

