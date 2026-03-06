import { useState, useEffect } from 'react'

export function useApi(fn, deps=[]){
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(()=>{
    let mounted = true
    setLoading(true); setError(null)
    fn().then(d => { if(mounted){ setData(d); setLoading(false) } }).catch(e=>{ if(mounted){ setError(e); setLoading(false) } })
    return ()=>{ mounted=false }
  // eslint-disable-next-line
  }, deps)

  return { data, loading, error }
}
