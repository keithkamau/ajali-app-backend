import { yupResolver } from '@hookform/resolvers/yup';
import { useForm } from 'react-hook-form';
import * as yup from 'yup';

const schema = yup.object({
  title: yup.string().trim().required('A title is required.').max(120, 'Use 120 characters or fewer.'),
  description: yup.string().trim().required('Please describe the incident.'),
  type: yup.string().required('Select an incident type.'),
  location_address: yup.string().trim().required('Add a location or address.'),
  location_lat: yup.number().typeError('Enter a valid latitude.').min(-90).max(90).required('Latitude is required.'),
  location_lng: yup.number().typeError('Enter a valid longitude.').min(-180).max(180).required('Longitude is required.'),
  is_anonymous: yup.boolean().default(false),
});

const incidentTypes = ['fire', 'medical', 'crime', 'accident', 'flood', 'other'];

export default function IncidentForm({ initialValues, onSubmit, submitting = false }) {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: yupResolver(schema),
    defaultValues: { is_anonymous: false, ...initialValues },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <label htmlFor="title">Title</label>
      <input id="title" {...register('title')} aria-invalid={Boolean(errors.title)} />
      {errors.title && <p role="alert">{errors.title.message}</p>}

      <label htmlFor="description">Description</label>
      <textarea id="description" rows="5" {...register('description')} aria-invalid={Boolean(errors.description)} />
      {errors.description && <p role="alert">{errors.description.message}</p>}

      <label htmlFor="type">Incident type</label>
      <select id="type" {...register('type')} aria-invalid={Boolean(errors.type)}>
        <option value="">Select a type</option>
        {incidentTypes.map((type) => <option key={type} value={type}>{type}</option>)}
      </select>
      {errors.type && <p role="alert">{errors.type.message}</p>}

      <label htmlFor="location_address">Location or address</label>
      <input id="location_address" {...register('location_address')} aria-invalid={Boolean(errors.location_address)} />
      {errors.location_address && <p role="alert">{errors.location_address.message}</p>}

      <label htmlFor="location_lat">Latitude</label>
      <input id="location_lat" type="number" step="any" {...register('location_lat')} aria-invalid={Boolean(errors.location_lat)} />
      {errors.location_lat && <p role="alert">{errors.location_lat.message}</p>}

      <label htmlFor="location_lng">Longitude</label>
      <input id="location_lng" type="number" step="any" {...register('location_lng')} aria-invalid={Boolean(errors.location_lng)} />
      {errors.location_lng && <p role="alert">{errors.location_lng.message}</p>}

      <label>
        <input type="checkbox" {...register('is_anonymous')} /> Submit anonymously
      </label>
      <button type="submit" disabled={submitting}>{submitting ? 'Submitting...' : 'Submit incident'}</button>
    </form>
  );
}
