Rails.application.routes.draw do
  namespace :api, defaults: { format: :json } do
    namespace :v1 do
      get  "health",          to: "health#index"
      post "auth/sign_up",    to: "auth#sign_up"
      post "auth/sign_in",    to: "auth#sign_in"

      resources :accounts,      only: %i[index show create update destroy]
      resources :categories,    only: %i[index show create update destroy]
      resources :transactions,  only: %i[index show create update destroy]
      resources :investments,   only: %i[index show create update destroy] do
        collection { get :portfolio }
      end
      resources :budgets,       only: %i[index show create update destroy] do
        collection { get :summary }
      end
    end
  end
end
